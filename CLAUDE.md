# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Full Stack FastAPI template combining:
- FastAPI backend with SQLModel (PostgreSQL)
- React frontend with TypeScript, Chakra UI, and TanStack tools
- Docker Compose for development and deployment
- JWT authentication, email recovery, and more

## Backend Commands

### Setup and Environment

```bash
# Set up backend development environment
cd backend
uv sync
source .venv/bin/activate

# Start the local stack with Docker Compose
docker compose watch

# Run prestart script
docker compose exec backend bash scripts/prestart.sh
```

### Tests

```bash
# Run backend tests
cd backend
bash ./scripts/test.sh

# Run backend tests with Docker Compose running
docker compose exec backend bash scripts/tests-start.sh

# Run tests with specific pytest options
docker compose exec backend bash scripts/tests-start.sh -x  # Stop on first error
```

### Database Migrations

```bash
# Create a new migration
docker compose exec backend bash -c "alembic revision --autogenerate -m 'Description of changes'"

# Apply migrations
docker compose exec backend bash -c "alembic upgrade head"
```

## Frontend Commands

```bash
# Set up frontend development environment
cd frontend
fnm use  # or nvm use
npm install

# Start frontend development server
npm run dev

# Build frontend
npm run build

# Lint frontend code
npm run lint

# Generate OpenAPI client
npm run generate-client
```

### End-to-End Tests

```bash
# Run Playwright tests
cd frontend
npx playwright test

# Run Playwright tests in UI mode
npx playwright test --ui
```

## Client Generation

Generate the frontend client from the OpenAPI schema:

```bash
# Automatically (recommended)
./scripts/generate-client.sh

# Or manually
# 1. Start Docker Compose stack
# 2. Download OpenAPI JSON from http://localhost/api/v1/openapi.json
# 3. Copy to frontend/openapi.json
# 4. Run:
cd frontend
npm run generate-client
```

## Architecture

### Backend

- **FastAPI with SQLModel**: Modern Python API framework with SQLAlchemy/Pydantic integration
- **Models**: Defined in `backend/app/models.py` for database tables
- **CRUD**: Database operations in `backend/app/crud.py`
- **API Routes**: Endpoints defined in `backend/app/api/routes/`
- **Core**: Configuration and core utilities in `backend/app/core/`
- **Alembic**: Database migrations

### Frontend

- **React 18**: With TypeScript and hooks
- **TanStack**: React Query for data fetching, TanStack Router for routing
- **Chakra UI**: Component library for styling
- **OpenAPI Client**: Auto-generated from backend schema

### Authentication

- JWT-based authentication with tokens
- Role-based access control
- Password reset via email

### Container Structure

- **Backend**: FastAPI application server
- **Frontend**: React SPA with Nginx
- **DB**: PostgreSQL database
- **Adminer**: Database admin tool
- **Traefik**: Reverse proxy for routing and HTTPS

## Development Flow

1. Start the Docker Compose stack with `docker compose watch`
2. Access services:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Swagger UI docs: http://localhost:8000/docs
   - Adminer: http://localhost:8080
3. For local frontend development:
   - `docker compose stop frontend`
   - `cd frontend && npm run dev`
4. For local backend development:
   - `docker compose stop backend`
   - `cd backend && fastapi dev app/main.py`

## Environment Configuration

Critical environment variables (in `.env`):
- `SECRET_KEY`: For security
- `FIRST_SUPERUSER_PASSWORD`: Initial admin password
- `POSTGRES_PASSWORD`: Database password

Generate secure keys with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```