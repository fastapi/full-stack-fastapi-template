# Setup Guide

Complete setup instructions for local development.

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- [uv](https://docs.astral.sh/uv/) for Python package management (backend)
- [Node.js](https://nodejs.org/) via nvm/fnm (frontend)
- Git
- [Supabase account](https://supabase.com/) - for managed PostgreSQL and Storage

## Supabase Setup

1. **Create a Supabase project**
   - Go to https://app.supabase.com and create a new project
   - Note down your project credentials from Settings → Database:
     - Project URL
     - API Keys (anon/public and service_role)
     - Database connection string (use **pooler** connection with **Transaction** mode)

2. **Configure Supabase in .env**
   ```bash
   # Get these from https://app.supabase.com/project/wijzypbstiigssjuiuvh/settings/database
   # Use SESSION MODE pooler (port 5432) for persistent Docker containers
   DATABASE_URL=postgresql+psycopg://postgres.wijzypbstiigssjuiuvh:YOUR-PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

   # Get these from https://app.supabase.com/project/wijzypbstiigssjuiuvh/settings/api
   SUPABASE_URL=https://wijzypbstiigssjuiuvh.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_KEY=your-service-role-key-here
   ```

   **Important**: Use **Session Mode** pooler (port 5432) for Docker Compose. This mode:
   - ✅ Supports prepared statements (faster queries)
   - ✅ Works with SQLAlchemy connection pooling
   - ✅ Best for persistent backends
   - ❌ Transaction Mode (port 6543) is only for serverless/edge functions

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CurriculumExtractor
   ```

2. **Configure environment variables**
   ```bash
   # Copy .env and update with your Supabase credentials
   # MUST change: DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
   # MUST change: SECRET_KEY, FIRST_SUPERUSER_PASSWORD, REDIS_PASSWORD
   ```

3. **Start with Docker Compose**
   ```bash
   docker compose watch
   ```

4. **Access the application**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **MailCatcher**: http://localhost:1080 (email testing)
   - **Traefik Dashboard**: http://localhost:8090
   - **Supabase Dashboard**: https://app.supabase.com/project/wijzypbstiigssjuiuvh
   
5. **Login**
   - Email: `admin@curriculumextractor.com`
   - Password: (from `FIRST_SUPERUSER_PASSWORD` in .env)

## Backend Setup (Local Development)

```bash
cd backend
uv sync                          # Install dependencies
source .venv/bin/activate        # Activate virtual environment
fastapi dev app/main.py          # Run development server
```

## Frontend Setup (Local Development)

```bash
cd frontend
fnm install                      # Install Node version from .nvmrc
fnm use                          # Switch to project Node version
npm install                      # Install dependencies
npm run dev                      # Start dev server
```

## Database Migrations

```bash
# Enter backend container
docker compose exec backend bash

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Environment Variables

Key variables to configure in `.env`:

**Supabase (REQUIRED)**:
- `DATABASE_URL` - Session Mode pooler connection (port 5432)
- `SUPABASE_URL` - Project URL (https://wijzypbstiigssjuiuvh.supabase.co)
- `SUPABASE_ANON_KEY` - Public API key (for frontend)
- `SUPABASE_SERVICE_KEY` - Admin API key (backend only, SECRET!)

**Redis + Celery (REQUIRED)**:
- `REDIS_PASSWORD` - Redis authentication password
- `REDIS_URL` - Redis connection (redis://:password@redis:6379/0)
- `CELERY_BROKER_URL` - Task queue broker
- `CELERY_RESULT_BACKEND` - Task result storage

**Security (MUST change for production)**:
- `SECRET_KEY` - JWT signing key (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `FIRST_SUPERUSER_PASSWORD` - Admin password
- `REDIS_PASSWORD` - Redis password

**Optional**:
- `SMTP_*` - Email configuration
- `SENTRY_DSN` - Error tracking

See `CLAUDE.md` for current configured values and complete list.

---

## Verifying Setup

After starting services, verify everything works:

```bash
# Check all services are healthy
docker compose ps

# Expected output:
# backend         - Up (healthy)
# frontend        - Up
# redis           - Up (healthy)
# celery-worker   - Up

# Test backend
curl http://localhost:8000/api/v1/utils/health-check/
# Should return: true

# Test Celery
curl -X POST http://localhost:8000/api/v1/tasks/health-check
# Should return: {"task_id": "...", "status": "queued"}

# Test frontend
curl http://localhost:5173
# Should return: HTML page

# Test Celery worker
docker compose logs celery-worker --tail=10
# Should show: "celery@... ready."
```

---

## Troubleshooting

### Docker Compose Issues
- Ensure Docker Desktop is running
- Check logs: `docker compose logs backend -f`
- Rebuild after changes: `docker compose build backend && docker compose up -d`
- Restart service: `docker compose restart backend`

### Database Connection Issues
- **Test connection via MCP**:
  ```python
  mcp_supabase_get_project(id="wijzypbstiigssjuiuvh")
  ```
- **Check logs**:
  ```bash
  docker compose logs backend | grep -i "database\|connection"
  ```
- **Verify credentials**: Check DATABASE_URL in .env
- **Common issues**:
  - Wrong password → Reset in Supabase dashboard
  - Wrong port → Use 5432 (Session Mode), not 6543 (Transaction Mode)
  - Wrong host → Use `aws-1-ap-south-1` (check your region)

### Celery Worker Not Starting
- Check Redis is healthy: `docker compose ps redis`
- Verify Redis password: `docker compose exec redis redis-cli -a YOUR-REDIS-PASSWORD PING`
- Check worker logs: `docker compose logs celery-worker --tail=50`
- Restart worker: `docker compose restart celery-worker`

### Frontend Not Loading
- Check backend is accessible: `curl http://localhost:8000/docs`
- Regenerate client: `./scripts/generate-client.sh`
- Clear node_modules: `rm -rf frontend/node_modules && cd frontend && npm install`
- Check TypeScript errors: `cd frontend && npx tsc --noEmit`

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :6379  # Redis

# Kill the process or change ports in docker-compose.override.yml
```

---

## Next Steps

After setup is complete:

1. **Test login**: http://localhost:5173
2. **Explore API**: http://localhost:8000/docs
3. **Review architecture**: [../architecture/overview.md](../architecture/overview.md)
4. **Start development**: [development.md](./development.md)
5. **Read PRD**: [../prd/overview.md](../prd/overview.md)

---

**Need help?** See [Supabase Setup Guide](./supabase-setup-guide.md) for detailed Supabase configuration.
