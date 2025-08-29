# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack FastAPI template with React frontend, built with modern tools and best practices. The project uses:
- **Backend**: FastAPI, SQLModel (Pydantic + SQLAlchemy), PostgreSQL
- **Frontend**: React, TypeScript, Vite, TanStack Router/Query, Chakra UI
- **DevOps**: Docker Compose, Traefik, GitHub Actions

## Quick Start Commands

### Development Environment
```bash
# Start the full stack with Docker Compose
docker compose watch

# URLs after starting:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Adminer (DB): http://localhost:8080
# Traefik UI: http://localhost:8090
```

### Backend Development
```bash
# Install dependencies and activate environment
cd backend
uv sync
source .venv/bin/activate

# Run backend locally (stop Docker service first)
docker compose stop backend
fastapi dev app/main.py

# Run backend tests
./scripts/test.sh  # or
uv run pytest

# Run specific test
uv run pytest tests/test_specific.py::test_function

# Database migrations
docker compose exec backend alembic revision --autogenerate -m "message"
docker compose exec backend alembic upgrade head
```

### Frontend Development
```bash
# Install dependencies and start dev server
cd frontend
npm install
npm run dev

# Generate API client after backend changes
./scripts/generate-client.sh

# Run frontend linting
npm run lint

# Run E2E tests
npx playwright test
npx playwright test --ui  # Interactive mode
```

## Architecture Overview

### Backend Structure
```
backend/
├── app/
│   ├── api/           # API routes organized by domain
│   ├── core/          # Configuration, security, database setup
│   ├── models.py      # SQLModel database models
│   ├── crud.py        # Reusable CRUD operations
│   └── tests/         # Pytest test files
└── scripts/           # Development and deployment scripts
```

### Frontend Structure
```
frontend/
├── src/
│   ├── client/        # Auto-generated OpenAPI client
│   ├── components/    # Reusable UI components
│   ├── routes/        # TanStack Router pages
│   └── hooks/         # Custom React hooks
└── tests/             # Playwright E2E tests
```

## Code Quality & Testing

### Backend
- **Linting**: Ruff (configured in pyproject.toml)
- **Type checking**: MyPy (strict mode)
- **Testing**: Pytest with coverage reports in `htmlcov/`
- **Pre-commit**: Runs ruff format, linting, and basic checks

### Frontend
- **Linting**: Biome (configured in biome.json)
- **Type checking**: TypeScript strict mode
- **Testing**: Playwright for E2E tests
- **Pre-commit**: Runs linting and formatting

## Common Development Tasks

### Adding a new API endpoint
1. Add model in `backend/app/models.py`
2. Create migration: `alembic revision --autogenerate -m "Add new model"`
3. Add CRUD operations in `backend/app/crud.py`
4. Add route in appropriate file under `backend/app/api/routes/`
5. Update frontend client: `./scripts/generate-client.sh`
6. Add frontend components/routes as needed

### Database changes
```bash
# Create migration after model changes
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migration
docker compose exec backend alembic upgrade head

# Check current revision
docker compose exec backend alembic current
```

### Environment Variables
Key variables in `.env`:
- `SECRET_KEY` - JWT secret (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `POSTGRES_PASSWORD` - Database password
- `FIRST_SUPERUSER_PASSWORD` - Initial admin password
- `DOMAIN` - For local testing with subdomains (e.g., `localhost.tiangolo.com`)

## Testing Commands

```bash
# Backend tests
./scripts/test.sh                    # All tests
uv run pytest tests/api/            # API tests only
uv run pytest -x                    # Stop on first failure
uv run pytest --cov=app             # With coverage

# Frontend tests
npm run test:e2e                    # Run Playwright tests
npm run test:e2e -- --ui           # Interactive mode
npm run test:e2e -- --debug        # Debug mode
```

## Deployment
See `deployment.md` for production deployment instructions using Docker Compose with Traefik for HTTPS.
