from rest_framework import serializers
from .models import Company, Job, JobApplication

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'website', 'logo', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'company_name', 'location', 'job_type', 'description', 
                 'requirements', 'salary_min', 'salary_max', 'application_url', 'source', 'status', 
                 'keywords', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)
    resume_title = serializers.CharField(source='resume.title', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = ['id', 'user', 'job', 'job_title', 'company_name', 'resume', 'resume_title', 
                 'cover_letter', 'status', 'applied_date', 'updated_at', 'match_score', 'notes']
        read_only_fields = ['id', 'user', 'applied_date', 'updated_at']