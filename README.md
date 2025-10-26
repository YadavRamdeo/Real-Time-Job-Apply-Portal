<img width="1568" height="762" alt="image" src="https://github.com/user-attachments/assets/dc88d863-64dc-4512-af0e-798c9d415b3b" />
# Real-Time Job Application Portal

A full-stack application built with Django and React that helps users find and automatically apply to jobs based on resume keyword matching.

## Features

- User authentication and profile management
- Resume upload and keyword extraction
- Real-time job search from company career pages
- Automatic job application based on resume keyword matching
- Real-time notifications for application status updates

## Setup Instructions

### Backend (Django)

1. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   cd backend
   python manage.py migrate
   ```

4. Start the server:
   ```
   python manage.py runserver
   ```

### Frontend (React)

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

## Project Structure

- `backend/` - Django backend application
- `frontend/` - React frontend application
