from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Company, Job, JobApplication
from .serializers import CompanySerializer, JobSerializer, JobApplicationSerializer
from .scraper import scrape_company_jobs, search_jobs_across_portals
from resumes.models import Resume
from resumes.matching import calculate_match_score, extract_skills_from_resume, preprocess_text
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_jobs(request):
    """Get all active jobs"""
    jobs = Job.objects.filter(status='active')
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_by_id(request, job_id):
    """Get job details by ID"""
    job = get_object_or_404(Job, id=job_id)
    serializer = JobSerializer(job)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_live_jobs(request):
    """Search real-time jobs across external portals (Indeed, Naukri, LinkedIn, remote boards),
    and optionally company ATS catalogs when available.

    Query params:
      - q | keywords | search: search keywords
      - location: location text (e.g., "India" or city)
      - country: country hint (default: India)
      - max: max items per portal (default: 10)
      - include_ats: 1/true to also search ATS catalogs if present (default: 1)
    """
    try:
        q = request.query_params.get('q') or request.query_params.get('keywords') or request.query_params.get('search') or ''
        location = request.query_params.get('location') or ''
        country = request.query_params.get('country') or 'India'
        try:
            max_per_portal = int(request.query_params.get('max') or 10)
        except Exception:
            max_per_portal = 10
        include_ats = str(request.query_params.get('include_ats', '1')).lower() in ['1', 'true', 'yes', 'on']

        results = search_jobs_across_portals(keywords=q, location=location, max_per_portal=max_per_portal, country=country)

        if include_ats:
            try:
                from pathlib import Path
                from .ats import load_company_catalog, scrape_companies_from_catalog
                base = Path(__file__).resolve().parent
                json_path = base / 'company_catalog.json'
                txt_path = base / 'company_catalog_urls.txt'
                catalog = load_company_catalog([str(json_path), str(txt_path)])
                if catalog:
                    ats_items = scrape_companies_from_catalog(catalog, max_per_company=10)
                    results.extend(ats_items)
            except Exception:
                pass

        # Dedupe by URL
        seen = set()
        deduped = []
        for it in results:
            url = it.get('application_url') if isinstance(it, dict) else None
            if not url or url in seen:
                continue
            seen.add(url)
            deduped.append(it)

        return Response(deduped)
    except Exception as e:
        logger.error(f"Error in live job search: {e}")
        return Response({"error": "Live search failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _keywords_from_resume(resume) -> str:
    """Build search keywords from resume parsed content (skills, languages, frameworks).
    Falls back to stored resume.skills, then generic defaults.
    """
    try:
        text = (getattr(resume, 'parsed_content', '') or '').strip()
        keywords: list[str] = []
        if text:
            # Prefer explicit skills extracted from the full resume text
            try:
                skills = extract_skills_from_resume(text)
                keywords.extend(skills or [])
            except Exception:
                pass
            # If still sparse, add top tokens by frequency (after preprocessing)
            if len(keywords) < 5:
                try:
                    from collections import Counter
                    tokens = (preprocess_text(text) or '').split()
                    common = [tok for tok, _ in Counter(tokens).most_common(12)]
                    keywords.extend([k for k in common if k not in keywords])
                except Exception:
                    pass
        # Fallback to structured resume.skills if present
        if not keywords:
            rs = getattr(resume, 'skills', None)
            if rs:
                if isinstance(rs, list):
                    keywords = [str(s) for s in rs if s]
                else:
                    try:
                        keywords = [str(rs)]
                    except Exception:
                        pass
        # Final fallback
        if not keywords:
            keywords = ['software', 'developer', 'engineer', 'python', 'django', 'react']
        return ' '.join(keywords[:12])
    except Exception:
        return 'software developer engineer python django react'

@api_view(['GET'])
def find_matching_jobs(request, resume_id):
    """Find jobs matching a resume.
    Accepts optional query param 'threshold' in range [0,1] (default: 0.3 if resume has content, else 0.0).
    Returns a list of { job, match_score } sorted descending.
    """
    try:
        resume = Resume.objects.get(id=resume_id)
        jobs = Job.objects.filter(status='active')

        # Determine threshold (default 60%)
        try:
            th_param = request.query_params.get('threshold')
            th = float(th_param) if th_param is not None else None
        except Exception:
            th = None
        threshold_percent = (th * 100.0) if th is not None else 60.0

        # Role filter: only software/CS engineering roles
        role_keywords = [
            'software engineer', 'software developer', 'developer', 'engineer', 'sde',
            'full stack', 'fullstack', 'backend', 'front end', 'frontend', 'web developer',
            'android', 'ios', 'mobile developer', 'devops', 'site reliability', 'sre',
            'data engineer', 'ml engineer', 'ai engineer', 'cloud engineer'
        ]
        def role_ok(title: str) -> bool:
            t = (title or '').lower()
            return any(tok in t for tok in role_keywords)
        
        # Calculate match scores for each job in DB first
        job_matches = []
        for job in jobs:
            if not role_ok(job.title):
                continue
            try:
                match_score = calculate_match_score(
                    resume.parsed_content or "",
                    job.description or "",
                    job.requirements or "",
                )
            except Exception:
                match_score = 0.0
            if match_score >= threshold_percent:
                job_matches.append({
                    'job': JobSerializer(job).data,
                    'match_score': round(match_score, 2)
                })

        # Also aggregate from external portals and ATS catalogs (no DB writes), and include
        try:
            from .ats import scrape_companies_from_catalog
            import json
            from pathlib import Path

            # Allow disabling external fetch for speed via ?external=0
            external_enabled = str(request.query_params.get('external', '0')).lower() in ['1','true','yes','on']
            external = []
            if external_enabled:
                external = search_jobs_across_portals(
                    keywords=_keywords_from_resume(resume),
                    location=request.query_params.get('location') or 'India',
                    country=request.query_params.get('country') or 'India',
                    max_per_portal=int(request.query_params.get('max') or 5),
                )
            # ATS catalog
            try:
                base = Path(__file__).resolve().parent
                json_path = base / 'company_catalog.json'
                txt_path = base / 'company_catalog_urls.txt'
                from .ats import load_company_catalog
                catalog = load_company_catalog([str(json_path), str(txt_path)])
                ats_items = scrape_companies_from_catalog(catalog, max_per_company=10)
                external.extend(ats_items)
            except Exception:
                pass

            for item in external:
                try:
                    title = item.get('title') or ''
                    if not role_ok(title):
                        continue
                    ms = calculate_match_score(
                        resume.parsed_content or '',
                        item.get('description') or '',
                        item.get('requirements') or ''
                    )
                    if ms >= threshold_percent:
                        job_matches.append({
                            'job': {
                                'title': title,
                                'company': {'name': item.get('company_name') or 'Unknown'},
                                'location': item.get('location') or '',
                                'job_type': item.get('job_type') or 'full_time',
                                'description': item.get('description') or '',
                                'requirements': item.get('requirements') or '',
                                'salary_min': item.get('salary_min'),
                                'salary_max': item.get('salary_max'),
                                'application_url': item.get('application_url'),
                                'source': item.get('source') or '',
                            },
                            'match_score': round(ms, 2)
                        })
                except Exception:
                    continue
        except Exception:
            pass
        
        # Sort by match score (highest first)
        job_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return Response(job_matches)
    except Resume.DoesNotExist:
        return Response(
            {"error": "Resume not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error finding matching jobs: {str(e)}")
        return Response(
            {"error": f"Error finding matching jobs: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_to_job(request, job_id):
    """Apply to a job with a resume"""
    try:
        job = Job.objects.get(id=job_id)
        resume_id = request.data.get('resume_id')
        
        if not resume_id:
            return Response(
                {"error": "Resume ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        resume = Resume.objects.get(id=resume_id)
        
        # Check if user owns this resume
        if resume.user != request.user:
            return Response(
                {"error": "You can only apply with your own resume"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Check if already applied
        existing_application = JobApplication.objects.filter(
            job=job, 
            resume=resume
        ).exists()
        
        if existing_application:
            return Response(
                {"error": "You have already applied to this job with this resume"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create application
        application = JobApplication.objects.create(
            job=job,
            resume=resume,
            status='applied'
        )
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Job.DoesNotExist:
        return Response(
            {"error": "Job not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Resume.DoesNotExist:
        return Response(
            {"error": "Resume not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error applying to job: {str(e)}")
        return Response(
            {"error": f"Error applying to job: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def scrape_jobs(self, request, pk=None):
        company = self.get_object()
        
        # Get optional parameters
        keywords = request.data.get('keywords', None)
        location = request.data.get('location', None)
        
        # Scrape jobs
        try:
            job_count = scrape_company_jobs(company.id, keywords, location)
            return Response({
                "status": "success",
                "message": f"Scraped {job_count} jobs for {company.name}"
            })
        except Exception as e:
            logger.error(f"Error scraping jobs: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Error scraping jobs: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Job.objects.filter(status='active')
        
        # Filter by search query
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(company__name__icontains=search)
            )
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by job type
        job_type = self.request.query_params.get('job_type', None)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Filter by salary range
        min_salary = self.request.query_params.get('min_salary', None)
        if min_salary:
            queryset = queryset.filter(salary_min__gte=min_salary)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job = self.get_object()
        
        # Get resume ID from request
        resume_id = request.data.get('resume_id')
        if not resume_id:
            return Response({
                "status": "error",
                "message": "Resume ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if resume exists and belongs to user
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Resume not found or does not belong to you"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already applied
        if JobApplication.objects.filter(user=request.user, job=job).exists():
            return Response({
                "status": "error",
                "message": "You have already applied for this job"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate match score
        match_score = calculate_match_score(
            resume.parsed_content,
            job.description,
            job.requirements
        )
        
        # Create job application
        cover_letter = request.data.get('cover_letter', '')
        application = JobApplication.objects.create(
            user=request.user,
            job=job,
            resume=resume,
            cover_letter=cover_letter,
            match_score=match_score
        )
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data)

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Get job and resume
        job_id = self.request.data.get('job')
        resume_id = self.request.data.get('resume')
        
        try:
            job = Job.objects.get(id=job_id)
            resume = Resume.objects.get(id=resume_id, user=self.request.user)
            
            # Calculate match score
            match_score = calculate_match_score(
                resume.parsed_content,
                job.description,
                job.requirements
            )
            
            serializer.save(user=self.request.user, match_score=match_score)
            
        except (Job.DoesNotExist, Resume.DoesNotExist) as e:
            logger.error(f"Error creating job application: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Error creating job application: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response({
                "status": "error",
                "message": "Status is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status
        application.status = status_value
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)