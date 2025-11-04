from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'get_skills_count')
    search_fields = ('user__username', 'user__email', 'title', 'parsed_content')
    list_filter = ('created_at', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'parsed_content', 'skills')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Resume File', {
            'fields': ('title', 'file', 'is_active')
        }),
        ('Parsed Data', {
            'fields': ('parsed_content', 'skills'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_skills_count(self, obj):
        if obj.skills:
            return len(obj.skills)
        return 0
    get_skills_count.short_description = 'Skills Count'
