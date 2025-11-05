#!/usr/bin/env python
"""Populate the database with sample data for testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from jobs.models import Company, Job
from django.contrib.auth.models import User

print("Creating sample data...")

# Create sample companies
companies_data = [
    {
        'name': 'Google',
        'website': 'https://careers.google.com',
        'description': 'Leading technology company focused on search, advertising, and cloud computing.'
    },
    {
        'name': 'Microsoft',
        'website': 'https://careers.microsoft.com',
        'description': 'Global technology company known for Windows, Office, and Azure.'
    },
    {
        'name': 'Amazon',
        'website': 'https://www.amazon.jobs',
        'description': 'E-commerce and cloud computing giant.'
    },
    {
        'name': 'Meta',
        'website': 'https://www.metacareers.com',
        'description': 'Social media and technology conglomerate.'
    },
    {
        'name': 'Apple',
        'website': 'https://www.apple.com/careers',
        'description': 'Innovative technology company known for iPhone, Mac, and services.'
    }
]

companies = []
for company_data in companies_data:
    company, created = Company.objects.get_or_create(
        name=company_data['name'],
        defaults={
            'website': company_data['website'],
            'description': company_data['description']
        }
    )
    companies.append(company)
    if created:
        print(f"✓ Created company: {company.name}")
    else:
        print(f"- Company already exists: {company.name}")

# Create sample jobs
jobs_data = [
    {
        'title': 'Senior Software Engineer',
        'company': companies[0],  # Google
        'location': 'Mountain View, CA',
        'job_type': 'full_time',
        'description': 'We are looking for a Senior Software Engineer to join our team. You will work on cutting-edge projects using the latest technologies.',
        'requirements': 'Requirements: 5+ years of experience in software development, Strong knowledge of Python, Java, or Go, Experience with distributed systems, BS in Computer Science or related field',
        'salary_min': 150000,
        'salary_max': 250000,
        'application_url': 'https://careers.google.com/jobs/12345',
        'keywords': ['python', 'java', 'distributed systems', 'software engineering'],
        'source': 'direct'
    },
    {
        'title': 'Frontend Developer',
        'company': companies[1],  # Microsoft
        'location': 'Redmond, WA',
        'job_type': 'full_time',
        'description': 'Join our team to build amazing user experiences. Work with React, TypeScript, and modern web technologies.',
        'requirements': 'Requirements: 3+ years of frontend development experience, Expert knowledge of React and TypeScript, Experience with responsive design, Strong CSS skills',
        'salary_min': 120000,
        'salary_max': 180000,
        'application_url': 'https://careers.microsoft.com/job/67890',
        'keywords': ['react', 'typescript', 'frontend', 'css', 'javascript'],
        'source': 'direct'
    },
    {
        'title': 'DevOps Engineer',
        'company': companies[2],  # Amazon
        'location': 'Seattle, WA',
        'job_type': 'full_time',
        'description': 'Build and maintain scalable infrastructure for AWS services. Work with cutting-edge cloud technologies.',
        'requirements': 'Requirements: 4+ years of DevOps experience, Strong knowledge of AWS, Docker, and Kubernetes, Experience with CI/CD pipelines, Python or Bash scripting',
        'salary_min': 140000,
        'salary_max': 200000,
        'application_url': 'https://www.amazon.jobs/en/jobs/11111',
        'keywords': ['aws', 'devops', 'kubernetes', 'docker', 'python'],
        'source': 'direct'
    },
    {
        'title': 'Full Stack Developer',
        'company': companies[3],  # Meta
        'location': 'Menlo Park, CA',
        'job_type': 'full_time',
        'description': 'Build full-stack applications that connect billions of people. Work with React, GraphQL, and backend services.',
        'requirements': 'Requirements: 3+ years of full stack experience, Proficiency in React and Node.js, Experience with GraphQL, Strong database knowledge (SQL and NoSQL)',
        'salary_min': 130000,
        'salary_max': 220000,
        'application_url': 'https://www.metacareers.com/jobs/22222',
        'keywords': ['react', 'nodejs', 'graphql', 'fullstack', 'javascript'],
        'source': 'direct'
    },
    {
        'title': 'iOS Developer',
        'company': companies[4],  # Apple
        'location': 'Cupertino, CA',
        'job_type': 'full_time',
        'description': 'Develop innovative iOS applications. Work on features used by millions of users worldwide.',
        'requirements': 'Requirements: 4+ years of iOS development experience, Expert knowledge of Swift and SwiftUI, Experience with UIKit, Strong understanding of Apple HIG',
        'salary_min': 140000,
        'salary_max': 210000,
        'application_url': 'https://jobs.apple.com/en-us/details/33333',
        'keywords': ['ios', 'swift', 'swiftui', 'mobile', 'xcode'],
        'source': 'direct'
    },
    {
        'title': 'Backend Engineer',
        'company': companies[0],  # Google
        'location': 'New York, NY',
        'job_type': 'full_time',
        'description': 'Build scalable backend services that power Google products. Work with microservices and cloud infrastructure.',
        'requirements': 'Requirements: 3+ years of backend development, Strong knowledge of Python or Java, Experience with microservices, Database design and optimization',
        'salary_min': 135000,
        'salary_max': 200000,
        'application_url': 'https://careers.google.com/jobs/44444',
        'keywords': ['python', 'java', 'backend', 'microservices', 'api'],
        'source': 'direct'
    },
    {
        'title': 'Data Engineer',
        'company': companies[2],  # Amazon
        'location': 'Austin, TX',
        'job_type': 'full_time',
        'description': 'Build data pipelines and analytics systems. Work with big data technologies and AWS.',
        'requirements': 'Requirements: 3+ years of data engineering experience, Strong SQL and Python skills, Experience with Spark and AWS data services, ETL pipeline development',
        'salary_min': 125000,
        'salary_max': 190000,
        'application_url': 'https://www.amazon.jobs/en/jobs/55555',
        'keywords': ['python', 'sql', 'spark', 'data engineering', 'etl', 'aws'],
        'source': 'direct'
    },
    {
        'title': 'Machine Learning Engineer',
        'company': companies[3],  # Meta
        'location': 'Remote',
        'job_type': 'remote',
        'description': 'Develop ML models that power recommendation systems. Work with PyTorch and large-scale data.',
        'requirements': 'Requirements: 4+ years of ML experience, Strong Python and PyTorch knowledge, Experience with recommendation systems, PhD or Masters in CS/ML preferred',
        'salary_min': 160000,
        'salary_max': 250000,
        'application_url': 'https://www.metacareers.com/jobs/66666',
        'keywords': ['python', 'pytorch', 'machine learning', 'ml', 'ai'],
        'source': 'direct'
    }
]

created_count = 0
for job_data in jobs_data:
    job, created = Job.objects.get_or_create(
        title=job_data['title'],
        company=job_data['company'],
        defaults=job_data
    )
    if created:
        print(f"✓ Created job: {job.title} at {job.company.name}")
        created_count += 1
    else:
        print(f"- Job already exists: {job.title} at {job.company.name}")

print(f"\n✅ Sample data creation complete!")
print(f"Companies: {len(companies)}")
print(f"Jobs created: {created_count}")
print(f"Total jobs: {Job.objects.count()}")
print("\nYou can now:")
print("1. View jobs in admin panel: http://localhost:8000/admin")
print("2. Access jobs via API: http://localhost:8000/api/jobs/")
