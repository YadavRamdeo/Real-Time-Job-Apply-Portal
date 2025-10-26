from rest_framework import serializers
from .models import Resume, JobPreference

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'user', 'title', 'file', 'parsed_content', 'skills', 'experience', 'education', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'parsed_content', 'skills', 'experience', 'education', 'created_at', 'updated_at']

class JobPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPreference
        fields = ['id', 'user', 'resume', 'job_titles', 'skills', 'locations', 'min_salary', 'remote_only', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']