from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_resumes, name='get_resumes'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('applications/', views.get_applications, name='get_applications'),
    path('applications/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
]