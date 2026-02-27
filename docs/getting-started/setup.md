---
title: "Setup Guide"
doc-type: how-to
status: published
last-updated: 2026-02-27
updated-by: "infra docs writer"
related-code:
  - backend/app/core/config.py
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

### Set Up Environment Variables

Create a `.env` file in the project root with required Supabase and Clerk credentials:

```bash
# Create .env file (note: .env is git-ignored)
cat > .env << 'EOF'
SUPABASE_URL=your-supabase-project-url
SUPABASE_SERVICE_KEY=your-supabase-service-key
CLERK_SECRET_KEY=your-clerk-secret-key
EOF
```

See the Environment Variables section below for complete configuration details.

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

Configuration is managed through environment variables loaded from the `.env` file. The application settings are **frozen and immutable** after initialization, and sensitive values use `SecretStr` type to prevent accidental logging.

### Required Variables (no defaults)

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | https://your-project.supabase.co |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | eyJhbGc... (long JWT) |
| `CLERK_SECRET_KEY` | Clerk secret key for JWT verification | sk_test_... |

### Optional Variables (with defaults)

| Variable | Default | Description | Notes |
|----------|---------|-------------|-------|
| `ENVIRONMENT` | local | Runtime environment | Values: `local`, `staging`, `production` |
| `SERVICE_NAME` | my-service | Application identifier | Used in logs and metrics |
| `SERVICE_VERSION` | 0.1.0 | Application version | Semantic versioning |
| `LOG_LEVEL` | INFO | Logging level | Values: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | json | Log output format | Values: `json`, `console` |
| `API_V1_STR` | /api/v1 | API prefix | Used for all API routes |
| `BACKEND_CORS_ORIGINS` | [] | Allowed CORS origins | Comma-separated or JSON array |
| `WITH_UI` | false | Include UI endpoints | Boolean: true/false |
| `CLERK_JWKS_URL` | None | Clerk JWKS endpoint | Auto-configured if not provided |
| `CLERK_AUTHORIZED_PARTIES` | [] | Authorized JWT audiences | List of allowed parties |
| `SENTRY_DSN` | None | Sentry error tracking | Optional error reporting URL |
| `GIT_COMMIT` | unknown | Current git commit hash | Automatically set by build system |
| `BUILD_TIME` | unknown | Build timestamp | Automatically set by build system |
| `HTTP_CLIENT_TIMEOUT` | 30 | HTTP request timeout (seconds) | For external API calls |
| `HTTP_CLIENT_MAX_RETRIES` | 3 | HTTP request retries | For resilience |

### Security Notes

- **Frozen settings**: All settings are immutable after the application starts. Configuration cannot be changed at runtime.
- **Secret values**: Variables containing secrets (ending in `_KEY` or `_SECRET`) use Pydantic's `SecretStr` type, which:
  - Prevents secret values from appearing in logs
  - Hides secrets in error messages and repr output
  - Must call `.get_secret_value()` to access actual value (framework handles this automatically)
- **Production validation**: In production environment, the application enforces:
  - Secret values cannot be `"changethis"` (will raise error on startup)
  - CORS origins cannot include wildcard `*` (will raise error on startup)
- **Local development**: Same validation applies, but `"changethis"` secrets emit warnings instead of errors

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
