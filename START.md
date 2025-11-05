# 🚀 Start Your Job Portal

Everything is installed and ready to go!

## ✅ Setup Complete

- ✅ Python dependencies installed
- ✅ Database migrated
- ✅ Superuser created
- ✅ Frontend dependencies installed

## 🔑 Admin Credentials

**Username:** `admin`  
**Password:** `admin123456`  
**Email:** admin@jobportal.com

⚠️ **Change this password after first login!**

## 🏃 Run the Application

### Option 1: Run Both Services (2 Terminals)

**Terminal 1 - Backend:**
```powershell
cd E:\Projects\Real-Time-Job-Apply-Portal\backend
python manage.py runserver
```

**Terminal 2 - Frontend:**
```powershell
cd E:\Projects\Real-Time-Job-Apply-Portal\frontend
npm start
```

### Option 2: Using Docker (Recommended)
```powershell
cd E:\Projects\Real-Time-Job-Apply-Portal
docker-compose up
```

## 🌐 Access the Application

Once both services are running:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api
- **Admin Panel:** http://localhost:8000/admin

## 📝 Quick Test

1. Go to http://localhost:3000
2. Register a new user account
3. Upload your resume
4. Search for jobs
5. Apply with one click!

## 🛠️ Development Commands

### Backend (Django)
```powershell
cd backend

# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Django shell
python manage.py shell

# Run tests
python manage.py test
```

### Frontend (React)
```powershell
cd frontend

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Ensure you're in the `backend` directory
- Run `python manage.py migrate` again

### Frontend won't start
- Check if port 3000 is already in use
- Delete `node_modules` and run `npm install` again
- Clear npm cache: `npm cache clean --force`

### Database issues
```powershell
cd backend
python manage.py migrate --run-syncdb
```

## 🎯 Next Steps

1. **Customize settings:** Edit `backend/jobportal/settings.py`
2. **Add companies:** Use admin panel to add companies
3. **Configure job sources:** Edit job scraping configuration
4. **Deploy:** See `DOCKER.md` for deployment instructions

---

**Need help?** Check the documentation or raise an issue on GitHub.
