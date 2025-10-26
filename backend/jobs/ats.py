import json
import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36'
HEADERS = {"User-Agent": USER_AGENT}

# ---- ATS DETECTORS ----

def is_greenhouse(url: str) -> bool:
    return 'greenhouse.io' in url or 'boards.greenhouse.io' in url


def is_lever(url: str) -> bool:
    return 'jobs.lever.co' in url or 'lever.co' in url


def is_smartrecruiters(url: str) -> bool:
    return 'smartrecruiters.com' in url


# ---- SCRAPERS ----

def scrape_greenhouse(career_url: str):
    """Scrape via Greenhouse Boards API when possible."""
    try:
        m = re.search(r"boards\.greenhouse\.io/([\w-]+)", career_url)
        company = m.group(1) if m else None
        if not company:
            # Try to discover board token from HTML
            html = requests.get(career_url, headers=HEADERS, timeout=15).text
            m = re.search(r"boards-api\.greenhouse\.io/v1/boards/([\w-]+)/", html)
            company = m.group(1) if m else None
        if not company:
            return []
        api = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
        resp = requests.get(api, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            return []
        data = resp.json()
        out = []
        for j in data.get('jobs', []):
            title = j.get('title')
            location = (j.get('location') or {}).get('name')
            url = j.get('absolute_url') or j.get('id')
            desc = j.get('content') or ''
            out.append({
                'title': title,
                'company_name': company.replace('-', ' ').title(),
                'location': location or '',
                'job_type': 'full_time',
                'description': desc,
                'requirements': '',
                'salary_min': None,
                'salary_max': None,
                'application_url': url if isinstance(url, str) else '',
                'keywords': [],
                'source': 'greenhouse'
            })
        return out
    except Exception as e:
        logger.error(f"Greenhouse scrape error: {e}")
        return []


def scrape_lever(career_url: str):
    try:
        m = re.search(r"lever\.co/([\w-]+)", career_url)
        company = m.group(1) if m else None
        if not company:
            # Try to find subdomain from HTML
            html = requests.get(career_url, headers=HEADERS, timeout=15).text
            m = re.search(r"api\.lever\.co/v0/postings/([\w-]+)", html)
            company = m.group(1) if m else None
        if not company:
            return []
        api = f"https://api.lever.co/v0/postings/{company}?mode=json"
        resp = requests.get(api, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            return []
        data = resp.json()
        out = []
        for j in data:
            out.append({
                'title': j.get('text'),
                'company_name': company.replace('-', ' ').title(),
                'location': (j.get('categories') or {}).get('location') or '',
                'job_type': 'full_time',
                'description': (j.get('lists') or [{}])[0].get('content') if j.get('lists') else '',
                'requirements': '',
                'salary_min': None,
                'salary_max': None,
                'application_url': j.get('hostedUrl') or j.get('applyUrl') or '',
                'keywords': [],
                'source': 'lever'
            })
        return out
    except Exception as e:
        logger.error(f"Lever scrape error: {e}")
        return []


def scrape_smartrecruiters(career_url: str):
    try:
        m = re.search(r"smartrecruiters\.com/([\w-]+)/?", career_url)
        company = m.group(1) if m else None
        if not company:
            return []
        api = f"https://api.smartrecruiters.com/v1/companies/{company}/postings"
        resp = requests.get(api, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            return []
        out = []
        for item in resp.json().get('content', []):
            title = item.get('name')
            loc = ((item.get('location') or {}).get('city') or '')
            url = (item.get('ref') or {}).get('jobAd') or ''
            desc = (item.get('jobAd') or {}).get('sections', {}).get('jobDescription', {}).get('text', '')
            out.append({
                'title': title,
                'company_name': company.replace('-', ' ').title(),
                'location': loc,
                'job_type': 'full_time',
                'description': desc,
                'requirements': '',
                'salary_min': None,
                'salary_max': None,
                'application_url': url,
                'keywords': [],
                'source': 'smartrecruiters'
            })
        return out
    except Exception as e:
        logger.error(f"SmartRecruiters scrape error: {e}")
        return []


def scrape_company_career(career_url: str):
    url = (career_url or '').lower()
    if is_greenhouse(url):
        return scrape_greenhouse(career_url)
    if is_lever(url):
        return scrape_lever(career_url)
    if is_smartrecruiters(url):
        return scrape_smartrecruiters(career_url)
    # Fallback: try to find obvious links
    try:
        html = requests.get(career_url, headers=HEADERS, timeout=15).text
        soup = BeautifulSoup(html, 'html.parser')
        # Try to find job cards quickly
        links = soup.select('a[href*="job"], a[href*="careers"], a[href*="opening"], a[href*="opportunity"]')
        out = []
        for a in links[:20]:
            href = a.get('href')
            if not href:
                continue
            if not href.startswith('http'):
                parsed = urlparse(career_url)
                href = f"{parsed.scheme}://{parsed.netloc}{href if href.startswith('/') else '/' + href}"
            out.append({
                'title': a.get_text(strip=True) or 'Job',
                'company_name': urlparse(career_url).netloc.split('.')[0].title(),
                'location': '',
                'job_type': 'full_time',
                'description': '',
                'requirements': '',
                'salary_min': None,
                'salary_max': None,
                'application_url': href,
                'keywords': [],
                'source': 'company'
            })
        return out
    except Exception:
        return []


def scrape_companies_from_catalog(catalog: list[dict], max_per_company: int = 10):
    all_jobs = []
    for entry in catalog:
        try:
            jobs = scrape_company_career(entry.get('career_url', ''))
            if jobs:
                all_jobs.extend(jobs[:max_per_company])
        except Exception:
            continue
    return all_jobs


def load_company_catalog(paths: list[str]) -> list[dict]:
    """Load company catalogs from JSON or TXT lines ("Name - URL")."""
    out: list[dict] = []
    seen = set()
    for p in paths:
        try:
            if p.endswith('.json'):
                import json
                with open(p, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                for it in items:
                    url = (it.get('career_url') or '').strip()
                    if url and url not in seen:
                        out.append({'name': it.get('name') or '', 'career_url': url})
                        seen.add(url)
            else:
                with open(p, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        # Expect: "Company - URL" or just URL
                        if ' - ' in line:
                            name, url = line.split(' - ', 1)
                        else:
                            name, url = '', line
                        url = url.strip()
                        if url and url not in seen:
                            out.append({'name': name.strip(), 'career_url': url})
                            seen.add(url)
        except Exception:
            continue
    return out
