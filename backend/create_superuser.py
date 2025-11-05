#!/usr/bin/env python
"""Create a superuser for the Job Portal"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
email = 'admin@jobportal.com'
password = 'admin123456'

if User.objects.filter(username=username).exists():
    print(f'Superuser "{username}" already exists!')
    user = User.objects.get(username=username)
    print(f'Email: {user.email}')
    print(f'Is superuser: {user.is_superuser}')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser created successfully!')
    print(f'Username: {username}')
    print(f'Email: {email}')
    print(f'Password: {password}')
    print('\n⚠️  IMPORTANT: Change this password after first login!')
