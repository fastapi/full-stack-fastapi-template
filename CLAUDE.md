# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full Stack FastAPI Template with React frontend. A production-ready template for building modern web applications with FastAPI backend and React frontend, using Docker Compose for both development and deployment.

**Tech Stack:**
- Backend: FastAPI, SQLModel (ORM), PostgreSQL, Alembic (migrations), JWT auth
- Frontend: React 19, TypeScript, Vite, TanStack Query/Router, Tailwind CSS, shadcn/ui
- Infrastructure: Docker Compose, Traefik (reverse proxy)
- Testing: Pytest (backend), Playwright (frontend E2E)

## Development Setup

### Starting the Stack

```bash
# Start full stack with hot reload
docker compose watch

# View logs
docker compose logs
docker compose logs backend  # specific service
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080
- Traefik UI: http://localhost:8090
- MailCatcher: http://localhost:1080

### Local Development (without Docker)

Stop a Docker service and run locally:

```bash
# Backend
docker compose stop backend
cd backend
fastapi dev app/main.py

# Frontend
docker compose stop frontend
cd frontend
npm run dev
```

## Backend Development

**Location:** `backend/app/`

### Common Commands

```bash
cd backend

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run tests with coverage
bash scripts/test.sh

# Run tests if stack is running
docker compose exec backend bash scripts/tests-start.sh

# Run tests with extra args (e.g., stop on first error)
docker compose exec backend bash scripts/tests-start.sh -x

# Format code
bash scripts/format.sh

# Lint code
bash scripts/lint.sh

# Run pre-commit hooks manually
uv run prek run --all-files
```

### Database Migrations

Use Alembic for all schema changes:

```bash
# Enter backend container
docker compose exec backend bash

# Create migration after model changes
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head
```

**Important:** Always create migrations when modifying models in `backend/app/models.py`. The application expects the database schema to match the models.

### Architecture

**Key Files:**
- `app/main.py` - FastAPI app initialization, CORS, Sentry
- `app/models.py` - SQLModel models (User, Item) with both ORM and Pydantic schemas
- `app/crud.py` - Database operations (create, read, update, delete)
- `app/api/main.py` - API router setup
- `app/api/routes/` - API endpoints organized by resource
- `app/api/deps.py` - FastAPI dependencies (DB session, auth, user injection)
- `app/core/config.py` - Settings management with Pydantic
- `app/core/security.py` - Password hashing, JWT token creation/validation
- `app/core/db.py` - Database engine and session setup

**Dependency Injection Pattern:**
- `SessionDep` - SQLModel database session
- `CurrentUser` - Authenticated user from JWT token
- `get_current_active_superuser` - Admin-only endpoints

**Model Pattern:**
SQLModel models use inheritance for different contexts:
- `Base` classes: Shared fields
- `Create` classes: API input for creation
- `Update` classes: API input for updates (optional fields)
- `Public` classes: API output (excludes sensitive fields)
- Table classes: Database models (e.g., `User(UserBase, table=True)`)

### Testing

Tests are in `backend/tests/`. Use pytest fixtures for database setup. Coverage reports are in `htmlcov/index.html`.

## Frontend Development

**Location:** `frontend/src/`

### Common Commands

```bash
cd frontend

# Install Node.js version (using fnm or nvm)
fnm install && fnm use

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Lint and format with Biome
npm run lint

# Run E2E tests
npx playwright test

# Run E2E tests in UI mode
npx playwright test --ui
```

### Generate Client

When backend OpenAPI schema changes, regenerate the frontend client:

```bash
# Automatic (requires backend venv activated)
./scripts/generate-client.sh

# Manual
# 1. Start Docker stack
# 2. Download http://localhost:8000/api/v1/openapi.json to frontend/openapi.json
# 3. cd frontend && npm run generate-client
```

**Important:** Regenerate after any backend API changes.

### Architecture

**Key Directories:**
- `src/routes/` - TanStack Router file-based routing with route components
- `src/components/` - Reusable React components
- `src/client/` - Auto-generated OpenAPI client (DO NOT EDIT)
- `src/hooks/` - Custom React hooks
- `src/assets/` - Static assets

**Routing:**
Uses TanStack Router with file-based routing:
- `__root.tsx` - Root layout
- `_layout.tsx` - Protected routes layout
- `_layout/index.tsx`, `_layout/items.tsx`, etc. - Protected pages
- `login.tsx`, `signup.tsx` - Public routes

**State Management:**
- TanStack Query for server state
- React Context for auth state
- Form state with react-hook-form + Zod validation

**Styling:**
Tailwind CSS with shadcn/ui components. Dark mode support via next-themes.

## Code Quality

### Pre-commit Hooks

Install `prek` (modern pre-commit alternative) to run linting/formatting before commits:

```bash
cd backend
uv run prek install -f
```

Hooks run automatically on `git commit`. Manual run:

```bash
cd backend
uv run prek run --all-files
```

**Configured Checks:**
- Ruff (Python linting and formatting)
- Biome (TypeScript/JavaScript linting and formatting)
- File checks (TOML, YAML, trailing whitespace, etc.)

## Environment Variables

Edit `.env` file for configuration. **Must change before deployment:**
- `SECRET_KEY` - JWT signing key
- `FIRST_SUPERUSER_PASSWORD` - Admin password
- `POSTGRES_PASSWORD` - Database password

Generate secure keys:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Testing with Custom Domains

For subdomain testing locally, use `localhost.tiangolo.com` (resolves to 127.0.0.1):

```bash
# Edit .env
DOMAIN=localhost.tiangolo.com

# Restart
docker compose watch
```

Access via:
- Frontend: http://dashboard.localhost.tiangolo.com
- Backend: http://api.localhost.tiangolo.com

## Deployment

See `deployment.md` for full deployment instructions. Quick overview:

```bash
# Build images
bash scripts/build.sh

# Build and push to registry
bash scripts/build-push.sh

# Deploy to server
bash scripts/deploy.sh
```

## Authentication Flow

1. User logs in via `/api/v1/login/access-token` with email/password
2. Backend validates credentials, returns JWT access token
3. Frontend stores token, includes in Authorization header
4. Backend validates JWT on protected routes via `get_current_user` dependency
5. User info injected into endpoint via `CurrentUser` dependency

## Key Patterns

**Backend:**
- Use `SessionDep` for database access in endpoints
- Use `CurrentUser` for authenticated user
- Create/update operations return full model objects
- All models use UUID primary keys
- Password hashing via passlib with bcrypt

**Frontend:**
- Use TanStack Query hooks for API calls
- Use generated client from `src/client/` for type-safe API calls
- Forms use react-hook-form with Zod schemas
- Protected routes check auth in layout
- Error boundaries for error handling
