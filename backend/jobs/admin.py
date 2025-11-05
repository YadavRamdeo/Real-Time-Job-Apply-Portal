from django.contrib import admin
from .models import Company, Job, JobApplication


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at')
    search_fields = ('name', 'website')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'status', 'created_at')
    search_fields = ('title', 'company__name', 'location', 'description')
    list_filter = ('status', 'job_type', 'created_at', 'company')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'location', 'job_type', 'status')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'keywords')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max')
        }),
        ('Application', {
            'fields': ('application_url', 'source')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'status', 'match_score', 'applied_date')
    search_fields = ('user__username', 'user__email', 'job__title', 'job__company__name')
    list_filter = ('status', 'applied_date')
    readonly_fields = ('applied_date', 'updated_at', 'match_score')
    fieldsets = (
        ('Application Info', {
            'fields': ('user', 'job', 'resume', 'status', 'match_score')
        }),
        ('Details', {
            'fields': ('cover_letter', 'notes')
        }),
        ('Timestamps', {
            'fields': ('applied_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
