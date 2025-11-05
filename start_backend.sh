#!/bin/bash
# Start Django backend server

echo "Starting Django backend..."
cd /mnt/e/Projects/Real-Time-Job-Apply-Portal

# Install dependencies if not already installed
if ! python3 -c "import django" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Navigate to backend and run server
cd backend
python3 manage.py runserver 0.0.0.0:8000
