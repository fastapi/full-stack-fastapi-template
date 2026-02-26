---
title: "Setup Guide"
doc-type: how-to
status: published
last-updated: 2026-02-26
updated-by: "initialise skill"
related-code:
  - .env
  - compose.yml
  - compose.override.yml
  - backend/Dockerfile
  - frontend/Dockerfile
  - backend/pyproject.toml
  - frontend/package.json
related-docs:
  - docs/getting-started/development.md
  - docs/getting-started/contributing.md
  - docs/deployment/environments.md
tags: [setup, onboarding, getting-started]
---

# Setup Guide

## Prerequisites

- Git
- Docker and Docker Compose (latest version)
- Python >=3.10 (for local backend development without Docker)
- Bun >=1.0 (for local frontend development without Docker)

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-org/your-repo.git
cd Aygentic-starter-template
```

### Copy Environment File

```bash
cp .env.example .env
# Edit .env with your local values (see Environment Variables section below)
```

### Start the Full Stack

The quickest way to get everything running is with Docker Compose:

```bash
docker compose watch
```

On first run, this will:
1. Build backend and frontend images
2. Start PostgreSQL database
3. Run database migrations via the `prestart` service
4. Start FastAPI backend server
5. Start Vite frontend dev server
6. Start Traefik proxy
7. Start Mailcatcher for email testing

The first startup takes ~1-2 minutes as the database initializes and migrations run.

### Verify Installation

Once `docker compose watch` shows services are running, open these URLs in your browser:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | React/TypeScript app |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| Database Admin | http://localhost:8080 | Adminer DB browser |
| Email Testing | http://localhost:1080 | Mailcatcher for captured emails |
| Proxy Dashboard | http://localhost:8090 | Traefik routing status |

### Run Tests to Verify Setup

Backend tests:

```bash
cd backend
bash ../scripts/test.sh
```

Frontend tests:

```bash
bunx playwright test
```

## Environment Variables

The `.env` file controls all configuration. Key variables for local development:

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `DOMAIN` | localhost | Yes | Used by Traefik for routing |
| `FRONTEND_HOST` | http://localhost:5173 | Yes | URL for backend to send emails |
| `ENVIRONMENT` | local | Yes | Set to: local, staging, production |
| `PROJECT_NAME` | Full Stack FastAPI Project | Yes | Shown in API docs and emails |
| `STACK_NAME` | full-stack-fastapi-project | Yes | Docker Compose labels (no spaces) |
| `BACKEND_CORS_ORIGINS` | http://localhost,http://localhost:5173 | Yes | Comma-separated allowed origins |
| `SECRET_KEY` | changethis | Yes | **Change this!** JWT signing key |
| `FIRST_SUPERUSER` | admin@example.com | Yes | First admin email |
| `FIRST_SUPERUSER_PASSWORD` | changethis | Yes | **Change this!** Admin password |
| `POSTGRES_SERVER` | localhost | Yes | DB hostname (db in Docker) |
| `POSTGRES_PORT` | 5432 | Yes | DB port |
| `POSTGRES_DB` | app | Yes | Database name |
| `POSTGRES_USER` | postgres | Yes | DB user |
| `POSTGRES_PASSWORD` | changethis | Yes | **Change this!** DB password |
| `SMTP_HOST` | [Optional] | No | Email server (uses Mailcatcher locally) |
| `SMTP_USER` | [Optional] | No | Email server username |
| `SMTP_PASSWORD` | [Optional] | No | Email server password |
| `EMAILS_FROM_EMAIL` | info@example.com | No | Sender email address |
| `SENTRY_DSN` | [Optional] | No | Sentry error tracking |

**For development**, the defaults are mostly fine. Change at minimum:
- `SECRET_KEY` - generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `FIRST_SUPERUSER_PASSWORD` - choose a password for admin login
- `POSTGRES_PASSWORD` - any secure string

## Working with Specific Services

### Stop/Start Services

To develop one component independently while Docker Compose runs everything else:

**Stop frontend in Docker, run locally:**

```bash
docker compose stop frontend
cd frontend
bun install
bun run dev
```

Frontend will still be at http://localhost:5173, but from your local Bun dev server instead of Docker.

**Stop backend in Docker, run locally:**

```bash
docker compose stop backend
cd backend
uv sync
fastapi dev app/main.py
```

Backend will be at http://localhost:8000 from your local uvicorn server.

**Stop specific service:**

```bash
docker compose stop db  # Stop database
docker compose logs backend  # View service logs
docker compose restart backend  # Restart service
```

## Database Setup

Migrations run automatically on startup via `docker compose`. To run manually:

```bash
cd backend
alembic upgrade head
```

To create a new migration after schema changes:

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5173 already in use | Kill the process: `lsof -ti:5173 \| xargs kill -9` or change in compose.override.yml |
| Port 8000 already in use | Kill the process: `lsof -ti:8000 \| xargs kill -9` or change in compose.override.yml |
| Port 5432 (database) already in use | Kill the process: `lsof -ti:5432 \| xargs kill -9` |
| Database connection refused | Wait 30+ seconds for `db` service healthcheck. Check logs: `docker compose logs db` |
| Migrations failing | Ensure `POSTGRES_PASSWORD` matches in .env. Drop and recreate: `docker compose down -v && docker compose up` |
| Backend/frontend not connecting | Verify `FRONTEND_HOST` and `BACKEND_CORS_ORIGINS` in .env. Check logs: `docker compose logs backend` |
| Mailcatcher not receiving emails | Check `SMTP_HOST` is set to `mailcatcher` in compose.override.yml (automatic) |
| `docker compose watch` not syncing code | Volumes mount correctly. Check logs: `docker compose logs backend` or `docker compose logs frontend` |

## Docker Compose Files

- **compose.yml** - Main config with db, backend, frontend, adminer, prestart
- **compose.override.yml** - Development overrides: ports, live reload, Traefik dashboard, Mailcatcher

After changing `.env`, restart the stack:

```bash
docker compose down && docker compose watch
```

## Next Steps

1. Read [Development Workflow](./development.md) to learn daily commands
2. Read [Contributing Guidelines](./contributing.md) for code standards
3. Check [Deployment Environments](../deployment/environments.md) to understand environments
4. Explore the [backend API docs](http://localhost:8000/docs) to see available endpoints

## Related

- [Development Workflow](./development.md)
- [Contributing Guidelines](./contributing.md)
- [Deployment Environments](../deployment/environments.md)
