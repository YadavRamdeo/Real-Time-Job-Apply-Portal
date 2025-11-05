import csv
import json
import re
from urllib.parse import urlparse
from pathlib import Path
from typing import Iterable, Tuple

from django.core.management.base import BaseCommand, CommandError
from jobs.models import Company


def _normalize_url(url: str) -> str:
    url = (url or '').strip()
    if not url:
        return ''
    if not re.match(r'^https?://', url, flags=re.I):
        url = 'https://' + url
    # Remove URL fragments and query for canonicalization
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = (parsed.path or '').rstrip('/')
    return f"https://{netloc}{path}" if netloc else url


def _name_from_url(url: str) -> str:
    try:
        host = urlparse(url).netloc
        if not host:
            return url
        host = host.lower()
        # strip common prefixes
        host = re.sub(r'^(www\d?\.|careers\.|jobs\.)', '', host)
        # take domain label
        label = host.split('.')
        if len(label) >= 2:
            return label[-2].capitalize()
        return host.capitalize()
    except Exception:
        return url


def _iter_from_csv(p: Path) -> Iterable[Tuple[str, str]]:
    with p.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Accept common header variants
        name_keys = {'name', 'company', 'company_name'}
        url_keys = {'website', 'url', 'career_url', 'careers_url'}
        headers = {h.lower(): h for h in reader.fieldnames or []}
        nk = next((headers[h] for h in headers if h in name_keys), None)
        uk = next((headers[h] for h in headers if h in url_keys), None)
        if not uk:
            raise CommandError('CSV must include a website/url/career_url column')
        for row in reader:
            raw_url = row.get(uk, '')
            url = _normalize_url(raw_url)
            name = row.get(nk) if nk else ''
            if not name:
                name = _name_from_url(url)
            if url:
                yield name.strip(), url


def _iter_from_json(p: Path) -> Iterable[Tuple[str, str]]:
    data = json.loads(p.read_text(encoding='utf-8'))
    if isinstance(data, dict):
        data = data.get('companies') or data.get('items') or []
    if not isinstance(data, list):
        raise CommandError('JSON must be an array or have a top-level "companies" list')
    for item in data:
        if not isinstance(item, dict):
            continue
        name = (item.get('name') or item.get('company') or '').strip()
        url = _normalize_url(item.get('website') or item.get('url') or item.get('career_url') or '')
        if not name:
            name = _name_from_url(url)
        if url:
            yield name, url


def _iter_from_txt(p: Path) -> Iterable[Tuple[str, str]]:
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        url = _normalize_url(line)
        name = _name_from_url(url)
        if url:
            yield name, url


class Command(BaseCommand):
    help = 'Import companies (name, website) from a CSV/JSON/TXT file into the database. Dedupe by website.'

    def add_arguments(self, parser):
        parser.add_argument('--file', '-f', required=True, help='Path to CSV/JSON/TXT file containing companies')
        parser.add_argument('--format', choices=['csv', 'json', 'txt'], help='Input format (auto-detected by extension if omitted)')
        parser.add_argument('--update-json', action='store_true', help='Also merge into jobs/company_catalog.json')
        parser.add_argument('--dry-run', action='store_true', help='Parse and report without writing to DB')

    def handle(self, *args, **opts):
        path = Path(opts['file']).expanduser().resolve()
        if not path.exists():
            raise CommandError(f'File not found: {path}')
        fmt = opts.get('format') or path.suffix.lower().lstrip('.')
        if fmt not in {'csv', 'json', 'txt'}:
            raise CommandError('Unsupported format. Use csv, json, or txt.')

        if fmt == 'csv':
            it = _iter_from_csv(path)
        elif fmt == 'json':
            it = _iter_from_json(path)
        else:
            it = _iter_from_txt(path)

        added = 0
        updated = 0
        seen = set()
        batch: list[tuple[str, str]] = []
        for name, url in it:
            key = _normalize_url(url)
            if not key or key in seen:
                continue
            seen.add(key)
            batch.append((name, key))

        if opts['dry_run']:
            self.stdout.write(self.style.WARNING(f'[dry-run] Parsed {len(batch)} unique entries'))
            for i, (name, url) in enumerate(batch[:10], 1):
                self.stdout.write(f'  {i}. {name} -> {url}')
            if len(batch) > 10:
                self.stdout.write(f'  ... and {len(batch)-10} more')
            return

        for name, url in batch:
            try:
                obj, created = Company.objects.update_or_create(
                    website=url,
                    defaults={'name': name},
                )
            except Company.MultipleObjectsReturned:
                # Merge duplicates by website
                dup_qs = Company.objects.filter(website=url).order_by('id')
                obj = dup_qs.first()
                # Remove extras
                dup_qs.exclude(id=obj.id).delete()
                created = False
            if created:
                added += 1
            else:
                if obj.name != name:
                    obj.name = name
                    obj.save(update_fields=['name'])
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f'Imported {len(batch)} entries: {added} added, {updated} updated'))

        if opts.get('update_json'):
            catalog_path = Path(__file__).parents[3] / 'jobs' / 'company_catalog.json'
            try:
                existing = []
                if catalog_path.exists():
                    existing = json.loads(catalog_path.read_text(encoding='utf-8'))
                # Merge, dedupe by career_url
                merged = {(item.get('career_url') or '').strip().lower(): item for item in existing if isinstance(item, dict)}
                for name, url in batch:
                    key = url.lower()
                    if not key:
                        continue
                    merged[key] = {"name": name, "career_url": url}
                out = [v for k, v in merged.items() if k]
                catalog_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
                self.stdout.write(self.style.SUCCESS(f'Updated catalog JSON at {catalog_path} ({len(out)} entries)'))
            except Exception as e:
                raise CommandError(f'Failed to update company_catalog.json: {e}')
