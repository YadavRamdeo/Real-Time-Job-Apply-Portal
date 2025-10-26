from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Resume, JobPreference
from .serializers import ResumeSerializer, JobPreferenceSerializer
from .matching import extract_skills_from_resume, extract_experience_from_resume
from jobs.models import Job, JobApplication
from jobs.serializers import JobSerializer, JobApplicationSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resumes(request):
    """Get all resumes for the current user"""
    resumes = Resume.objects.filter(user=request.user)
    serializer = ResumeSerializer(resumes, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_resume(request):
    """Upload a new resume and auto-search/apply to matching jobs."""
    serializer = ResumeSerializer(data=request.data)
    if serializer.is_valid():
        resume = serializer.save(user=request.user)
        auto_apply_summary = {"total_found": 0, "applied": 0, "errors": 0}
        
        # Parse resume content and auto-apply
        try:
            parsed_content = request.data.get('content', '')
            # Extract skills and experience
            skills = extract_skills_from_resume(parsed_content)
            experience = extract_experience_from_resume(parsed_content)
            # Update resume with parsed data
            resume.parsed_content = parsed_content
            resume.skills = skills
            resume.experience = experience
            resume.save()

            # Auto-search and apply
            from jobs.scraper import search_jobs_across_portals
            from jobs.models import Company, Job, JobApplication
            from resumes.matching import calculate_match_score
            from accounts.models import Notification

            keywords = " ".join(skills) if skills else ""
            location = request.data.get('location', '')
            search_results = search_jobs_across_portals(
                keywords=keywords or 'software engineer developer sde',
                location=location or 'India',
                country='India',
                max_per_portal=5,
            )
            auto_apply_summary["total_found"] = len(search_results)

            for item in search_results:
                try:
                    # Ensure company exists
                    company_name = item.get('company_name') or (item.get('company').name if item.get('company') else 'Unknown')
                    website = {
                        'indeed': 'https://www.indeed.com',
                        'naukri': 'https://www.naukri.com',
                        'linkedin': 'https://www.linkedin.com'
                    }.get(item.get('source'), '')
                    company, _ = Company.objects.get_or_create(name=company_name, defaults={'website': website})

                    # Create or update job entry
                    job, _ = Job.objects.update_or_create(
                        title=item['title'],
                        company=company,
                        application_url=item['application_url'],
                        defaults={
                            'location': item.get('location') or '',
                            'job_type': item.get('job_type') or 'full_time',
                            'description': item.get('description') or '',
                            'requirements': item.get('requirements') or '',
                            'salary_min': item.get('salary_min'),
                            'salary_max': item.get('salary_max'),
                            'keywords': item.get('keywords') or [],
                            'status': 'active',
                        }
                    )

                    # Compute match
                    match_score = calculate_match_score(
                        resume.parsed_content or '',
                        job.description or '',
                        job.requirements or ''
                    )
                    if match_score < 60.0:
                        continue

                    # Skip if already applied
                    if JobApplication.objects.filter(user=request.user, job=job, resume=resume).exists():
                        continue

                    # Create application as "applied"
                    JobApplication.objects.create(
                        user=request.user,
                        job=job,
                        resume=resume,
                        cover_letter='',
                        status='applied',
                        match_score=match_score
                    )

                    # Notify user
                    try:
                        Notification.objects.create(
                            user=request.user,
                            title=f"Applied: {job.title}",
                            message=f"Automatically applied to {job.title} at {company.name}.",
                        )
                    except Exception:
                        pass

                    auto_apply_summary["applied"] += 1
                except Exception as e:
                    logger.error(f"Auto-apply error: {str(e)}")
                    auto_apply_summary["errors"] += 1
        except Exception as e:
            logger.error(f"Error parsing resume/auto-applying: {str(e)}")
        
        data = serializer.data
        data["auto_apply_summary"] = auto_apply_summary
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_applications(request):
    """Get all job applications for the current user"""
    # Get all resumes for this user
    resumes = Resume.objects.filter(user=request.user)
    
    # Get all applications for these resumes
    applications = JobApplication.objects.filter(resume__in=resumes)
    serializer = JobApplicationSerializer(applications, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_application_status(request, application_id):
    """Update the status of a job application"""
    try:
        application = JobApplication.objects.get(id=application_id)
        
        # Check if user owns this application
        if application.resume.user != request.user:
            return Response(
                {"error": "You can only update your own applications"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update status
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {"error": "Status is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = new_status
        application.save()
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data)
    except JobApplication.DoesNotExist:
        return Response(
            {"error": "Application not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        resume = serializer.save(user=self.request.user)
        
        # Parse resume content
        try:
            # In a real application, you would use a PDF parser or similar
            # For this example, we'll assume the content is already parsed
            parsed_content = "Sample parsed content from resume"
            
            # Extract skills and experience
            skills = extract_skills_from_resume(parsed_content)
            experience = extract_experience_from_resume(parsed_content)
            
            # Update resume with parsed data
            resume.parsed_content = parsed_content
            resume.skills = skills
            resume.experience = experience
            resume.save()
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
    
    @action(detail=True, methods=['get'])
    def matching_jobs(self, request, pk=None):
        resume = self.get_object()
        
        # Get all active jobs
        jobs = Job.objects.filter(status='active')
        
        # Find matching jobs
        from resumes.matching import find_matching_jobs
        matching_jobs = find_matching_jobs(resume, jobs)
        
        # Prepare response
        job_data = []
        for match in matching_jobs:
            job_serializer = JobSerializer(match['job'])
            job_data.append({
                'job': job_serializer.data,
                'match_score': match['match_score']
            })
        
        return Response(job_data)

class JobPreferenceViewSet(viewsets.ModelViewSet):
    queryset = JobPreference.objects.all()
    serializer_class = JobPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Ensure the resume belongs to the user
        resume_id = self.request.data.get('resume')
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=self.request.user)
                serializer.save(user=self.request.user, resume=resume)
            except Resume.DoesNotExist:
                return Response(
                    {"error": "Resume not found or does not belong to you"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Resume ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )