# Quick Start with Docker

Simple guide to run the Job Portal using Docker with SQLite3.

## Prerequisites

- Docker Desktop installed on Windows
- Git (to clone if needed)

## Start the Application

### 1. Start all services

```powershell
docker-compose up --build
```

Wait for all services to start. You should see:
- ✅ Redis running on port 6379
- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000

### 2. Access the application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

### 3. Create an admin user (optional)

In a new terminal:

```powershell
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Common Commands

### Stop everything
```powershell
docker-compose down
```

### Restart services
```powershell
docker-compose restart
```

### View logs
```powershell
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend
```

### Clean database and start fresh
```powershell
docker-compose down -v
docker-compose up --build
```

## Database Location

Your SQLite3 database is stored in:
- `backend/db.sqlite3` (persisted on your local machine)

All uploaded resumes and media files are in:
- `backend/media/` (persisted on your local machine)

## Troubleshooting

### Port already in use

If port 3000 or 8000 is already taken, stop other services or change ports in `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Change 3001 to any free port
```

### Backend not starting

Check if migrations are needed:

```powershell
docker-compose exec backend python manage.py migrate
```

### Frontend build issues

Rebuild the frontend:

```powershell
docker-compose build --no-cache frontend
docker-compose up frontend
```

## Development Tips

### Running locally (without Docker)

**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```powershell
cd frontend
npm install
npm start
```

### Database shell access

```powershell
docker-compose exec backend python manage.py dbshell
```

### Django shell access

```powershell
docker-compose exec backend python manage.py shell
```

## What's Running?

| Service  | Port | Purpose                          |
|----------|------|----------------------------------|
| Frontend | 3000 | React UI                        |
| Backend  | 8000 | Django REST API + WebSockets    |
| Redis    | 6379 | Channel layers for WebSockets   |

Database: **SQLite3** (simple, file-based, no extra setup needed)

## Next Steps

1. Register a user account at http://localhost:3000/register
2. Upload your resume
3. Search for jobs
4. Apply with one click!

---

**Need help?** Check the full documentation in `DOCKER.md`
