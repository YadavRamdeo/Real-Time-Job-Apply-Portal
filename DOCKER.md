# Docker Setup Guide

This guide will help you run the Real-Time Job Apply Portal using Docker.

## Prerequisites

- Docker Desktop (for Windows)
- Docker Compose

## Quick Start

### 1. Build and Start All Services

```bash
docker-compose up --build
```

This will start:
- **Backend** (Django + Daphne): http://localhost:8000
- **Frontend** (React + Nginx): http://localhost:3000
- **Redis**: localhost:6379
- **Celery Worker**: Background task processing

### 2. Run Database Migrations

In a new terminal, run:

```bash
docker-compose exec backend python manage.py migrate
```

### 3. Create a Superuser (Optional)

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

## Useful Commands

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Clean Database)
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery
```

### Restart a Service
```bash
docker-compose restart backend
```

### Run Django Commands
```bash
docker-compose exec backend python manage.py <command>
```

### Access Backend Shell
```bash
docker-compose exec backend python manage.py shell
```

### Run Tests
```bash
docker-compose exec backend python manage.py test
```

## Development Mode

For development, you can run services individually:

### Backend Only
```bash
docker-compose up backend redis
```

### Frontend Only (with local backend)
```bash
cd frontend
npm start
```

## Production Deployment

For production:

1. Update environment variables in `docker-compose.yml` or use `.env` file
2. Set `DEBUG=False`
3. Change `SECRET_KEY` to a strong random value
4. Configure `ALLOWED_HOSTS` properly
5. Use a production-grade database (PostgreSQL)
6. Enable SSL/HTTPS
7. Set up proper logging and monitoring

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Maps host 8001 to container 8000
```

### Database Issues
If you encounter database issues, reset the database:

```bash
docker-compose down -v
docker-compose up --build
docker-compose exec backend python manage.py migrate
```

### Permission Issues (Linux/Mac)
If you encounter permission issues with SQLite:

```bash
docker-compose exec backend chown -R 1000:1000 /app
```

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
┌──────▼──────┐ ┌───▼────────┐
│  Frontend   │ │  Backend   │
│  (Nginx)    │ │  (Daphne)  │
│  Port 3000  │ │  Port 8000 │
└─────────────┘ └─────┬──────┘
                      │
                ┌─────┴─────┬────────┐
                │           │        │
         ┌──────▼──────┐ ┌──▼───┐ ┌─▼──────┐
         │   Celery    │ │Redis │ │SQLite3 │
         │   Worker    │ │      │ │  (Vol) │
         └─────────────┘ └──────┘ └────────┘
```

## Notes

- SQLite database is persisted in a Docker volume named `sqlite_data`
- Media files are stored in `media_files` volume
- Static files are stored in `static_files` volume
- Redis is used for WebSocket channels and Celery task queue
