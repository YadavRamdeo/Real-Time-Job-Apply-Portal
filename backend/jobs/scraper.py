import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from datetime import datetime
from .models import Company, Job

logger = logging.getLogger(__name__)

class JobScraper:
    """Base class for job scrapers"""
    
    def __init__(self, company):
        self.company = company
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_keywords(self, text):
        """Extract keywords from job description"""
        # Remove HTML tags
        clean_text = re.sub(r'<.*?>', ' ', text)
        # Remove special characters and extra spaces
        clean_text = re.sub(r'[^\w\s]', ' ', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip().lower()
        
        # Extract common job skills and keywords
        skills = []
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'django',
            'flask', 'spring', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'git', 'agile', 'scrum',
            'machine learning', 'data science', 'ai', 'devops', 'frontend', 'backend',
            'fullstack', 'mobile', 'android', 'ios', 'swift', 'kotlin', 'react native',
            'flutter', 'ui/ux', 'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind',
            'typescript', 'c#', 'c++', 'php', 'ruby', 'rails', 'go', 'rust', 'scala'
        ]
        
        for skill in common_skills:
            if skill in clean_text:
                skills.append(skill)
        
        return skills

    @staticmethod
    def is_cs_role(title: str) -> bool:
        """Basic filter for software/CS roles by title"""
        t = (title or '').lower()
        role_tokens = [
            'software engineer', 'software developer', 'developer', 'engineer', 'sde',
            'full stack', 'fullstack', 'backend', 'front end', 'frontend', 'web developer',
            'android', 'ios', 'mobile developer', 'devops', 'site reliability', 'sre',
            'data engineer', 'ml engineer', 'ai engineer', 'cloud engineer'
        ]
        return any(tok in t for tok in role_tokens)
    
    def scrape_jobs(self):
        """Method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement scrape_jobs method")


class LinkedInScraper(JobScraper):
    """Scraper for LinkedIn job listings"""
    
    def scrape_jobs(self, keywords=None, location=None):
        jobs = []
        
        try:
            # Build search URL
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                "keywords": keywords or "",
                "location": location or "",
                "f_C": self.company.name,
                "trk": "jobs_jserp_search_button_execute",
                "pageNum": 0
            }
            
            response = requests.get(base_url, params=params, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"Failed to fetch LinkedIn jobs: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='job-search-card')
            
            for card in job_cards:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    link_elem = card.find('a', class_='base-card__full-link')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    
                    if not all([title_elem, link_elem, company_elem, location_elem]):
                        continue
                    
                    job_url = link_elem['href']
                    
                    # Get job details
                    job_response = requests.get(job_url, headers=self.headers)
                    if job_response.status_code != 200:
                        continue
                    
                    job_soup = BeautifulSoup(job_response.text, 'html.parser')
                    description_elem = job_soup.find('div', class_='show-more-less-html__markup')
                    
                    if not description_elem:
                        continue
                    
                    description = description_elem.get_text(strip=True)
                    requirements = ""
                    
                    # Try to extract requirements section
                    req_section = job_soup.find('h3', string=re.compile(r'Requirements|Qualifications', re.I))
                    if req_section and req_section.find_next('ul'):
                        requirements = req_section.find_next('ul').get_text(strip=True)
                    
                    # Extract job type
                    job_type = 'full_time'  # Default
                    job_type_elem = job_soup.find('span', string=re.compile(r'Employment type', re.I))
                    if job_type_elem and job_type_elem.find_next('span'):
                        job_type_text = job_type_elem.find_next('span').get_text(strip=True).lower()
                        if 'part' in job_type_text:
                            job_type = 'part_time'
                        elif 'contract' in job_type_text:
                            job_type = 'contract'
                        elif 'intern' in job_type_text:
                            job_type = 'internship'
                        elif 'remote' in job_type_text:
                            job_type = 'remote'
                    
                    # Extract salary if available
                    salary_min = None
                    salary_max = None
                    salary_elem = job_soup.find('span', string=re.compile(r'Salary', re.I))
                    if salary_elem and salary_elem.find_next('span'):
                        salary_text = salary_elem.find_next('span').get_text(strip=True)
                        salary_match = re.search(r'(\$[\d,]+)\s*-\s*(\$[\d,]+)', salary_text)
                        if salary_match:
                            salary_min = int(salary_match.group(1).replace('$', '').replace(',', ''))
                            salary_max = int(salary_match.group(2).replace('$', '').replace(',', ''))
                    
                    # Extract keywords
                    keywords = self.extract_keywords(description + " " + requirements)
                    
                    job = {
                        'title': title_elem.get_text(strip=True),
                        'company': self.company,
                        'location': location_elem.get_text(strip=True),
                        'job_type': job_type,
                        'description': description,
                        'requirements': requirements,
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'application_url': job_url,
                        'keywords': keywords
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Error processing job card: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {str(e)}")
            return jobs


class IndeedScraper(JobScraper):
    """Scraper for Indeed job listings"""
    
    def scrape_jobs(self, keywords=None, location=None, country: str | None = None):
        jobs = []
        
        try:
            # Build search URL (use India domain when requested)
            in_india = (country or '').lower() == 'india' or (location or '').lower() in ['india', 'in']
            base_url = "https://in.indeed.com/jobs" if in_india else "https://www.indeed.com/jobs"
            params = {
                "q": keywords or "",
                "l": (location or ("India" if in_india else "")),
                "sort": "date"
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to fetch Indeed jobs: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    link_elem = card.find('a', class_='jcs-JobTitle')
                    company_elem = card.find('span', class_='companyName')
                    location_elem = card.find('div', class_='companyLocation')
                    
                    if not all([title_elem, link_elem, company_elem, location_elem]):
                        continue
                    
                    job_id = link_elem.get('data-jk', '')
                    job_url = f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else link_elem.get('href')
                    if not job_url:
                        continue
                    
                    description = ''
                    requirements = ''
                    job_type = 'full_time'
                    salary_min = None
                    salary_max = None
                    
                    # Extract keywords
                    kws = self.extract_keywords((title_elem.get_text(strip=True) or '') + ' ' + (company_elem.get_text(strip=True) or ''))
                    
                    job = {
                        'title': title_elem.get_text(strip=True),
                        'company_name': company_elem.get_text(strip=True),
                        'location': location_elem.get_text(strip=True),
                        'job_type': job_type,
                        'description': description,
                        'requirements': requirements,
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'application_url': job_url,
                        'keywords': kws
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Error processing Indeed job card: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {str(e)}")
            return jobs

class NaukriScraper(JobScraper):
    """Scraper for Naukri.com listings"""
    
    def scrape_jobs(self, keywords=None, location=None, country: str | None = None):
        jobs = []
        try:
            # Construct a simple search URL
            kw = (keywords or '').strip().replace(' ', '-')
            loc = (location or '').strip().replace(' ', '-')
            url = f"https://www.naukri.com/{kw}-jobs-in-{loc}" if kw and loc else f"https://www.naukri.com/{kw}-jobs" if kw else "https://www.naukri.com/jobs"
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch Naukri jobs: {resp.status_code}")
                return jobs
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Naukri uses multiple layouts; try generic card selectors
            cards = soup.select('article.jobTuple, div.list > div.cardWrapper')
            if not cards:
                cards = soup.find_all('div', class_=re.compile(r'jdwhtw|cust-job-tuple'))
            for card in cards:
                try:
                    title_elem = card.find(['a','span'], attrs={'title': True}) or card.find('a', href=True)
                    company_elem = card.find('a', attrs={'class': re.compile(r'comp|company')}) or card.find('span', string=re.compile(r'Ltd|Inc|Pvt|Company', re.I))
                    location_elem = card.find('li', class_=re.compile(r'location', re.I)) or card.find('span', class_=re.compile(r'loc'))
                    link = None
                    if title_elem and title_elem.get('href'):
                        link = title_elem.get('href')
                    elif card.find('a', href=True):
                        link = card.find('a', href=True)['href']
                    if not (title_elem and company_elem and link):
                        continue
                    title = title_elem.get_text(strip=True)
                    company_name = company_elem.get_text(strip=True)
                    loc_text = location_elem.get_text(strip=True) if location_elem else ''
                    job = {
                        'title': title,
                        'company_name': company_name,
                        'location': loc_text,
                        'job_type': 'full_time',
                        'description': '',
                        'requirements': '',
                        'salary_min': None,
                        'salary_max': None,
                        'application_url': link,
                        'keywords': self.extract_keywords(title)
                    }
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Error processing Naukri job card: {str(e)}")
                    continue
            return jobs
        except Exception as e:
            logger.error(f"Naukri scraping error: {str(e)}")
            return jobs

def search_jobs_across_portals(keywords: str, location: str | None = None, max_per_portal: int = 10, country: str = 'India', role_keywords: list[str] | None = None):
    """Search jobs on supported portals and return a combined list of dictionaries.
    This function is best-effort and resilient to scraping issues.
    """
    results = []
    try:
        # Normalize role keywords
        role_keywords = role_keywords or [
            'software engineer', 'software developer', 'developer', 'engineer', 'sde',
            'full stack', 'fullstack', 'backend', 'front end', 'frontend', 'web developer',
            'android', 'ios', 'mobile developer', 'devops', 'site reliability', 'sre',
            'data engineer', 'ml engineer', 'ai engineer', 'cloud engineer'
        ]
        def role_ok(title: str) -> bool:
            t = (title or '').lower()
            return any(tok in t for tok in role_keywords)

        # Helper to record with source
        def add_items(items, source):
            for it in items:
                it['source'] = source
            return items

        # Indeed
        try:
            indeed = IndeedScraper(Company(name='Indeed', website='https://www.indeed.com'))
            items = indeed.scrape_jobs(keywords=keywords, location=location, country=country)[:max_per_portal]
            results.extend([it for it in add_items(items, 'indeed') if role_ok(it.get('title'))])
        except Exception as e:
            logger.error(f"Indeed search error: {e}")
        # Naukri
        try:
            naukri = NaukriScraper(Company(name='Naukri', website='https://www.naukri.com'))
            items = naukri.scrape_jobs(keywords=keywords, location=location or 'india', country=country)[:max_per_portal]
            results.extend([it for it in add_items(items, 'naukri') if role_ok(it.get('title'))])
        except Exception as e:
            logger.error(f"Naukri search error: {e}")
        # WeWorkRemotely
        try:
            url = "https://weworkremotely.com/categories/remote-programming-jobs"
            resp = requests.get(url, headers={"User-Agent": JobScraper(None).headers['User-Agent']}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                lis = soup.select('section.jobs li.feature, section.jobs li:not(.view-all)')
                cnt = 0
                for li in lis:
                    if cnt >= max_per_portal: break
                    a = li.find('a', href=True)
                    if not a: continue
                    title = (a.find('span', class_='title').get_text(strip=True) if a.find('span', class_='title') else a.get_text(strip=True))
                    company = (a.find('span', class_='company').get_text(strip=True) if a.find('span', class_='company') else 'Unknown')
                    if not role_ok(title):
                        continue
                    results.append({
                        'title': title,
                        'company_name': company,
                        'location': 'Remote',
                        'job_type': 'remote',
                        'description': '',
                        'requirements': '',
                        'salary_min': None,
                        'salary_max': None,
                        'application_url': 'https://weworkremotely.com' + a['href'],
                        'keywords': [],
                        'source': 'weworkremotely'
                    })
                    cnt += 1
        except Exception as e:
            logger.error(f"WWR search error: {e}")
        # RemoteOK (simple HTML list)
        try:
            resp = requests.get('https://remoteok.com/remote-dev-jobs', headers={"User-Agent": JobScraper(None).headers['User-Agent']}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                rows = soup.select('table#jobsboard tr.job')[:max_per_portal]
                for row in rows:
                    title = (row.find('h2') or row.find('td', class_='company_and_position')).get_text(strip=True)
                    if not role_ok(title):
                        continue
                    comp = (row.find('h3') or row.find('td', class_='company')).get_text(strip=True) if (row.find('h3') or row.find('td', class_='company')) else 'Unknown'
                    link = row.get('data-href') or (row.find('a', href=True)['href'] if row.find('a', href=True) else '')
                    if link and not link.startswith('http'):
                        link = 'https://remoteok.com' + link
                    results.append({
                        'title': title,
                        'company_name': comp,
                        'location': 'Remote',
                        'job_type': 'remote',
                        'description': '',
                        'requirements': '',
                        'salary_min': None,
                        'salary_max': None,
                        'application_url': link,
                        'keywords': [],
                        'source': 'remoteok'
                    })
        except Exception as e:
            logger.error(f"RemoteOK search error: {e}")
        # Remotive
        try:
            resp = requests.get('https://remotive.com/remote-jobs/software-dev', headers={"User-Agent": JobScraper(None).headers['User-Agent']}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                cards = soup.select('div.job-tile')[:max_per_portal]
                for c in cards:
                    a = c.find('a', href=True)
                    title = c.find('span', class_='font-weight-bold').get_text(strip=True) if c.find('span', class_='font-weight-bold') else (a.get_text(strip=True) if a else '')
                    if not role_ok(title):
                        continue
                    comp = c.find('span', class_='company')
                    results.append({
                        'title': title,
                        'company_name': comp.get_text(strip=True) if comp else 'Unknown',
                        'location': 'Remote',
                        'job_type': 'remote',
                        'description': '',
                        'requirements': '',
                        'salary_min': None,
                        'salary_max': None,
                        'application_url': ('https://remotive.com' + a['href']) if a and a['href'].startswith('/') else (a['href'] if a else ''),
                        'keywords': [],
                        'source': 'remotive'
                    })
        except Exception as e:
            logger.error(f"Remotive search error: {e}")
        # LinkedIn (best-effort)
        try:
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                "keywords": keywords or "",
                "location": location or (country or ""),
                "trk": "jobs_jserp_search_button_execute",
                "pageNum": 0
            }
            resp = requests.get(base_url, params=params, headers={"User-Agent": JobScraper(None).headers['User-Agent']}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                cards = soup.find_all('div', class_='job-search-card')
                for card in cards[:max_per_portal]:
                    try:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        link_elem = card.find('a', class_='base-card__full-link')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        location_elem = card.find('span', class_='job-search-card__location')
                        if not all([title_elem, link_elem, company_elem]):
                            continue
                        t = title_elem.get_text(strip=True)
                        if not role_ok(t):
                            continue
                        results.append({
                            'title': t,
                            'company_name': company_elem.get_text(strip=True),
                            'location': location_elem.get_text(strip=True) if location_elem else '',
                            'job_type': 'full_time',
                            'description': '',
                            'requirements': '',
                            'salary_min': None,
                            'salary_max': None,
                            'application_url': link_elem['href'],
                            'keywords': [],
                            'source': 'linkedin'
                        })
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
    finally:
        # Dedupe by URL
        seen = set()
        deduped = []
        for it in results:
            url = it.get('application_url')
            if not url or url in seen:
                continue
            seen.add(url)
            deduped.append(it)
        return deduped


def scrape_company_jobs(company_id, keywords=None, location=None):
    """Scrape jobs for a specific company"""
    try:
        company = Company.objects.get(id=company_id)
        
        # Choose scraper based on company website
        if 'linkedin.com' in company.website:
            scraper = LinkedInScraper(company)
        elif 'indeed.com' in company.website:
            scraper = IndeedScraper(company)
        else:
            # Default to LinkedIn
            scraper = LinkedInScraper(company)
        
        jobs_data = scraper.scrape_jobs(keywords, location)
        
        # Save jobs to database
        for job_data in jobs_data:
            Job.objects.update_or_create(
                title=job_data['title'],
                company=job_data['company'],
                application_url=job_data['application_url'],
                defaults={
                    'location': job_data['location'],
                    'job_type': job_data['job_type'],
                    'description': job_data['description'],
                    'requirements': job_data['requirements'],
                    'salary_min': job_data['salary_min'],
                    'salary_max': job_data['salary_max'],
                    'keywords': job_data['keywords'],
                    'status': 'active'
                }
            )
        
        return len(jobs_data)
    
    except Company.DoesNotExist:
        logger.error(f"Company with ID {company_id} does not exist")
        return 0
    except Exception as e:
        logger.error(f"Error scraping jobs: {str(e)}")
        return 0