from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_jobs, name='get_jobs'),
    path('search/', views.search_live_jobs, name='search_live_jobs'),
    path('<int:job_id>/', views.get_job_by_id, name='get_job_by_id'),
    path('matching/<int:resume_id>/', views.find_matching_jobs, name='find_matching_jobs'),
    path('apply/<int:job_id>/', views.apply_to_job, name='apply_to_job'),
]
