from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='resumes/')
    parsed_content = models.TextField(blank=True, null=True)
    skills = models.JSONField(default=list)
    experience = models.JSONField(default=list)
    education = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class JobPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_preferences')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='job_preferences')
    job_titles = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    locations = models.JSONField(default=list)
    min_salary = models.IntegerField(null=True, blank=True)
    remote_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job Preferences - {self.user.username}"