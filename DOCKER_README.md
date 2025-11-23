# Site Generator - Docker Setup

## Quick Start

### Prerequisites

- Docker Desktop installed
- Docker Compose V2

### Development Setup

1. **Start all services:**

```bash
docker-compose up -d
```

2. **View logs:**

```bash
docker-compose logs -f
```

3. **Access services:**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

4. **Stop services:**

```bash
docker-compose down
```

5. **Stop and remove volumes (⚠️ deletes database):**

```bash
docker-compose down -v
```

## Service Management

### Backend (Django)

**Run migrations:**

```bash
docker-compose exec backend python manage.py migrate
```

**Create superuser:**

```bash
docker-compose exec backend python manage.py createsuperuser
```

**Collect static files:**

```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

**Access Django shell:**

```bash
docker-compose exec backend python manage.py shell
```

### Frontend (React)

**Install new package:**

```bash
docker-compose exec frontend npm install <package-name>
```

**Rebuild frontend:**

```bash
docker-compose exec frontend npm run build
```

### Database

**Access PostgreSQL:**

```bash
docker-compose exec db psql -U postgres -d sitegenerator
```

**Backup database:**

```bash
docker-compose exec db pg_dump -U postgres sitegenerator > backup.sql
```

**Restore database:**

```bash
docker-compose exec -T db psql -U postgres sitegenerator < backup.sql
```

### Redis

**Access Redis CLI:**

```bash
docker-compose exec redis redis-cli
```

**Monitor Redis:**

```bash
docker-compose exec redis redis-cli MONITOR
```

## Troubleshooting

### Rebuild containers:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### View container logs:

```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
docker-compose logs redis
docker-compose logs celery
```

### Restart specific service:

```bash
docker-compose restart backend
```

### Check service health:

```bash
docker-compose ps
```

### Clean up everything:

```bash
docker-compose down -v --rmi all
```

## Environment Variables

Create `.env` file in project root with:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=sitegenerator
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgres://postgres:postgres@db:5432/sitegenerator

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Frontend
VITE_API_URL=http://localhost:8000
```

## Production Deployment

1. Update environment variables for production
2. Use production Dockerfile (to be created)
3. Set DEBUG=0
4. Configure proper ALLOWED_HOSTS
5. Use volume mounts for media files
6. Set up nginx for static file serving
7. Use gunicorn instead of runserver
8. Enable SSL/TLS

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React/Vite)  │
│   Port: 5173    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   Backend       │────▶│  PostgreSQL  │
│   (Django)      │     │  Port: 5432  │
│   Port: 8000    │     └──────────────┘
└────────┬────────┘
         │              ┌──────────────┐
         └─────────────▶│    Redis     │
                        │  Port: 6379  │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Celery    │
                        │   Worker     │
                        └──────────────┘
```

## Volume Mounts

- `postgres_data`: PostgreSQL database files
- `redis_data`: Redis persistence
- `media_files`: User uploaded files
- `static_files`: Collected static files
- `./backend`: Backend source (development)
- `./frontend`: Frontend source (development)

## Network

All services run on a custom bridge network `sitegen_network` for inter-service communication.

## Health Checks

All services have health checks configured:

- Backend: HTTP check on port 8000
- Frontend: HTTP check on port 5173
- PostgreSQL: pg_isready
- Redis: redis-cli ping

## Common Issues

**Port already in use:**

- Stop the service using the port or change the port mapping in docker-compose.yml

**Database connection refused:**

- Wait for PostgreSQL health check to pass
- Check DATABASE_URL environment variable

**Frontend can't connect to backend:**

- Verify VITE_API_URL is correct
- Check CORS_ALLOWED_ORIGINS includes frontend URL

**Celery not processing tasks:**

- Check CELERY_BROKER_URL and REDIS_URL
- View celery logs: `docker-compose logs celery`
