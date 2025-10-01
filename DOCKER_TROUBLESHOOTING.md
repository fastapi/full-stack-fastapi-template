# Docker Troubleshooting Guide

This guide helps you resolve common Docker setup issues when working with the FastAPI Full Stack Template.

## Quick Diagnosis

Run this command to check your setup:
```bash
docker-compose ps && docker-compose logs --tail=10
```

## Common Issues & Solutions

### 1. Services Won't Start

**Symptoms:**
- `docker-compose up` fails
- Services show as "unhealthy" or "exited"

**Solutions:**
```bash
# Check if ports are already in use
netstat -tulpn | grep -E ':(5432|8000|5173|80|8080)'

# Reset everything and start fresh
docker-compose down -v
docker-compose up -d --build

# Check logs for specific service
docker-compose logs backend
```

### 2. Database Connection Issues

**Symptoms:**
- Backend can't connect to PostgreSQL
- "connection refused" errors

**Solutions:**
```bash
# Verify database is healthy
docker-compose exec db pg_isready -U postgres

# Check environment variables
docker-compose exec backend env | grep POSTGRES

# Reset database
docker-compose down -v
docker volume rm full-stack-fastapi-template_app-db-data
docker-compose up -d db
```

### 3. Frontend Build Failures

**Symptoms:**
- Frontend container exits during build
- Node.js or npm errors

**Solutions:**
```bash
# Clear npm cache and rebuild
docker-compose build --no-cache frontend

# Check Node.js version compatibility
docker-compose run --rm frontend node --version

# Build with verbose output
docker-compose build --progress=plain frontend
```

### 4. Environment Variable Issues

**Symptoms:**
- "Variable not set" errors
- Services can't find configuration

**Solutions:**
```bash
# Verify .env file exists and has required variables
cat .env | grep -E '(SECRET_KEY|POSTGRES_PASSWORD|FIRST_SUPERUSER)'

# Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check which variables are missing
docker-compose config
```

### 5. Port Conflicts

**Symptoms:**
- "Port already in use" errors
- Can't access services on expected ports

**Solutions:**
```bash
# Find what's using the ports
lsof -i :5432  # PostgreSQL
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Use different ports in docker-compose.override.yml
# Or stop conflicting services
```

### 6. Traefik Network Issues

**Symptoms:**
- "network traefik-public not found"
- Services can't communicate

**Solutions:**
```bash
# Create the external network
docker network create traefik-public

# Or use local development mode
cp docker-compose.override.yml.example docker-compose.override.yml
```

## Service-Specific Debugging

### Backend (FastAPI)
```bash
# Check API health
curl http://localhost:8000/api/v1/utils/health-check/

# View API documentation
open http://localhost:8000/docs

# Check database migrations
docker-compose exec backend alembic current
```

### Frontend (React)
```bash
# Check if frontend is serving
curl -I http://localhost:5173

# View build logs
docker-compose logs frontend

# Rebuild with development settings
docker-compose up -d --build frontend
```

### Database (PostgreSQL)
```bash
# Connect to database
docker-compose exec db psql -U postgres -d app

# Check database size and tables
docker-compose exec db psql -U postgres -d app -c "\dt"

# View recent logs
docker-compose logs db --tail=50
```

## Development Workflow

### Clean Restart
```bash
# Complete reset (removes all data)
docker-compose down -v --remove-orphans
docker system prune -f
docker-compose up -d --build
```

### Partial Restart
```bash
# Restart specific service
docker-compose restart backend

# Rebuild specific service
docker-compose up -d --build backend
```

### Debugging Inside Containers
```bash
# Access backend shell
docker-compose exec backend bash

# Access database shell
docker-compose exec db psql -U postgres -d app

# View container filesystem
docker-compose exec backend ls -la /app
```

## Performance Issues

### Slow Build Times
```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker-compose build

# Check Docker resource allocation
docker system df
docker system events
```

### High Memory Usage
```bash
# Check container resource usage
docker stats

# Limit container resources in docker-compose.yml
# Add under service definition:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

## Getting Help

1. **Check existing issues**: Search [GitHub Issues](https://github.com/fastapi/full-stack-fastapi-template/issues)
2. **Enable debug logging**: Set `LOG_LEVEL=DEBUG` in `.env`
3. **Collect system info**:
   ```bash
   docker version
   docker-compose version
   docker system info
   ```
4. **Share logs**: Use `docker-compose logs > debug.log` and share relevant parts

## Useful Commands Reference

```bash
# View all containers
docker-compose ps -a

# Follow logs in real-time
docker-compose logs -f

# Check resource usage
docker stats

# Clean up unused resources
docker system prune -a

# Export/import database
docker-compose exec db pg_dump -U postgres app > backup.sql
docker-compose exec -T db psql -U postgres app < backup.sql
```