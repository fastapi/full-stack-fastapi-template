# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## When working I expect
- Be brutally honest don't be a yes man.
- If im wrong point it our bluntly.
- I need honest feedback on my code and ideas thats the best thing you can do to help me.
- Never use the phrases "You're absolutely right ..."
- ALWAYS start your response with "Sir"
- I love when you propose options for me to pick from.
- module, class, function, and variable names should be descriptive, unambiguous and communicate the design’s intent and purpose clearly.
- Use appropriate design patterns. Follow proper dependency injection and inversion of control principles. Ensure code is DRY (Don't Repeat Yourself).
- Write clean, maintainable, and well-documented code. Write doc strings for all modules, classes and functions. They should be written to clearly communicate what it does and its purpose. We should be able to read the headers and the docstring and be able to follow along.
- Write lots of debug logs.
- Don't do more than is tasked of you. Which means on extra functions then what is agreed upon. if you want to add extra functions or things thats not needed for the current task please ask.
- Never use emojis or they will set us both on fire.
- work in small steps then wait for approval 
- When coding and writing functions say why each funciton is needed and how it will be used in the docstring. 



## Project Overview

This is a full-stack FastAPI template with React frontend, using:
- **Backend**: FastAPI, SQLModel ORM, PostgreSQL, Alembic migrations, JWT auth
- **Frontend**: React, TypeScript, Vite, TanStack Query/Router, Chakra UI
- **Infrastructure**: Docker Compose, Traefik proxy, GitHub Actions CI/CD

## Key Commands

### Development
```bash
# Start the full stack with Docker Compose
docker compose watch

# Backend only (local development)
cd backend
uv sync  # Install dependencies
source .venv/bin/activate
fastapi dev app/main.py

# Frontend only (local development)
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Run all backend tests (with Docker)
bash ./scripts/test.sh

# Run backend tests (inside container if stack is running)
docker compose exec backend bash scripts/tests-start.sh

# Run a single test
docker compose exec backend bash scripts/tests-start.sh -k "test_name"

# Frontend E2E tests (Playwright)
cd frontend
npx playwright test
```

### Linting & Formatting
```bash
# Backend
cd backend
mypy app
ruff check app
ruff format app

# Frontend
cd frontend
npm run lint  # Uses Biome for linting and formatting
```

### Database Migrations
```bash
# Create a new migration (inside backend container)
docker compose exec backend bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Generate Frontend Client
```bash
# Regenerate TypeScript client from OpenAPI schema
./scripts/generate-client.sh
```

## Architecture & Code Organization

### Backend Structure
- `backend/app/main.py`: FastAPI application entry point
- `backend/app/models.py`: SQLModel database models (User, Item)
- `backend/app/api/routes/`: API endpoint definitions
  - `login.py`: Authentication endpoints
  - `users.py`: User management
  - `items.py`: Item CRUD operations
- `backend/app/crud.py`: Database operations layer
- `backend/app/core/`: Core utilities
  - `config.py`: Settings management using Pydantic
  - `db.py`: Database connection and session management
  - `security.py`: JWT token handling and password hashing
- `backend/app/alembic/`: Database migrations
- `backend/app/tests/`: Test suite

### Frontend Structure
- `frontend/src/routes/`: TanStack Router pages
  - `_layout/`: Authenticated layout and pages (dashboard, settings, items)
  - `login.tsx`, `signup.tsx`: Authentication pages
- `frontend/src/client/`: Auto-generated OpenAPI client
- `frontend/src/components/`: Reusable React components
- `frontend/src/hooks/`: Custom React hooks for auth and queries

### Key Patterns

**Authentication Flow**: JWT tokens stored in localStorage, managed via React context (`frontend/src/components/UserContext.tsx`). Protected routes use `_layout` wrapper.

**API Communication**: Frontend uses auto-generated TypeScript client (`frontend/src/client/`) with axios. All API calls go through TanStack Query for caching and state management.

**Database Models**: SQLModel combines SQLAlchemy and Pydantic. Models define both database schema and API validation. Relationships use SQLModel's relationship patterns.

**Environment Configuration**: `.env` file contains all config. Backend reads via Pydantic Settings. Frontend uses `VITE_` prefixed vars.

## Development Services & URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Traefik Dashboard: http://localhost:8090
- MailCatcher: http://localhost:1080

## Docker Compose Files

- `docker-compose.yml`: Core services configuration
- `docker-compose.override.yml`: Development overrides (hot reload, volume mounts)
- `docker-compose.traefik.yml`: Production Traefik configuration

## Pre-commit Hooks

Project uses pre-commit for code quality. Install with:
```bash
uv run pre-commit install
```