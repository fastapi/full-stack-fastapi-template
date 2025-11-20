# LesMee Development Environment

This guide covers how to set up and use the LesMee development environment using Docker Compose.

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git

### Setup
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd lesmee-full

# Start the development environment
docker-compose -f docker-compose.dev.yml --env-file .env.dev up --build -d
```

### Access Services
Once started, you can access:
- **Frontend**: http://localhost:5173 (React/Vite with hot reload)
- **Backend API**: http://localhost:8000 (FastAPI with auto-reload)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/api/v1/utils/health-check/ (Database + Redis status)

## Services Overview

### Database (PostgreSQL)
- **Port**: 5432
- **Host**: localhost
- **Database**: lesmee_dev
- **Username**: postgres
- **Password**: postgres123

Connect with your favorite PostgreSQL client (DBeaver, pgAdmin, TablePlus, etc.)

### Redis
- **Port**: 6379
- **Host**: localhost
- **Password**: redis123

Use Redis CLI or Redis GUI tools like RedisInsight.

### Backend (FastAPI)
- **Port**: 8000
- **Auto-reload**: Enabled
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/utils/health-check/

### Frontend (React/Vite)
- **Port**: 5173
- **Hot Reload**: Enabled
- **Dev Server**: Vite development server

## Development Workflow

### Making Changes
1. **Backend**: Edit files in `./backend/` - changes trigger automatic reload
2. **Frontend**: Edit files in `./frontend/` - changes trigger hot reload via Vite

### Environment Variables
Edit `.env.dev` to customize development settings:
- Database credentials
- Redis configuration
- Admin user credentials
- CORS origins

### Database Management
```bash
# Access database container
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d lesmee_dev

# Run migrations manually
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Create new migration
docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "description"
```

### Redis Management
```bash
# Access Redis CLI
docker-compose -f docker-compose.dev.yml exec redis redis-cli

# Authenticate with password
AUTH redis123
```

## Useful Commands

### Environment Management
```bash
# Start development environment
./scripts/dev-start.sh

# Stop development environment
./scripts/dev-stop.sh

# View logs for all services
docker-compose -f docker-compose.dev.yml logs -f

# View logs for specific service
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend
docker-compose -f docker-compose.dev.yml logs -f db
docker-compose -f docker-compose.dev.yml logs -f redis
```

### Container Management
```bash
# Rebuild specific service
docker-compose -f docker-compose.dev.yml up --build -d backend

# Restart specific service
docker-compose -f docker-compose.dev.yml restart backend

# Execute commands in containers
docker-compose -f docker-compose.dev.yml exec backend bash
docker-compose -f docker-compose.dev.yml exec frontend sh
```

### Cleaning Up
```bash
# Stop and remove containers, networks, volumes
docker-compose -f docker-compose.dev.yml down -v

# Remove all unused Docker resources
docker system prune -a --volumes
```

## Default Credentials

### Admin User
- **Email**: admin@lesmee.dev
- **Password**: admin123

### Database
- **Host**: localhost
- **Port**: 5432
- **Database**: lesmee_dev
- **Username**: postgres
- **Password**: postgres123

### Redis
- **Host**: localhost
- **Port**: 6379
- **Password**: redis123

## Troubleshooting

### Port Conflicts
If ports are already in use, modify them in `docker-compose.dev.yml`:
```yaml
ports:
  - "5433:5432"  # PostgreSQL on 5433
  - "6380:6379"  # Redis on 6380
```

### Permission Issues
If you encounter permission errors, ensure Docker has proper permissions and consider:
```bash
# Fix Docker permissions on Linux/Mac
sudo chown -R $USER:$USER ./
```

### Backend Build Issues
If backend fails to start:
1. Check logs: `docker-compose -f docker-compose.dev.yml logs backend`
2. Ensure `.env.dev` exists and is correctly configured
3. Try rebuilding: `docker-compose -f docker-compose.dev.yml up --build -d backend`

### Frontend Build Issues
If frontend fails to start:
1. Check logs: `docker-compose -f docker-compose.dev.yml logs frontend`
2. Ensure node_modules volume is properly mounted
3. Try rebuilding: `docker-compose -f docker-compose.dev.yml up --build -d frontend`

## Development Best Practices

1. **Use Version Control**: Commit changes frequently with descriptive messages
2. **Environment Variables**: Keep sensitive data in `.env.dev`, don't commit it
3. **Database Migrations**: Always create migrations for schema changes
4. **Code Quality**: Use linters and formatters configured in the project
5. **Testing**: Run tests before committing changes
6. **Documentation**: Update this file when making architectural changes

## Production Deployment

For production deployment, use the main `docker-compose.yml` file with Traefik reverse proxy, not this development setup.

## Need Help?

- Check the logs for detailed error messages
- Refer to the main project documentation
- Open an issue in the project repository