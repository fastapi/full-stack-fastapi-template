# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack FastAPI + React application with:
- **Backend**: FastAPI, SQLModel, PostgreSQL, Alembic, JWT auth
- **Frontend**: React, TypeScript, Vite, TanStack Query/Router, Chakra UI
- **Infrastructure**: Docker Compose, Traefik proxy

## Essential Commands

### Backend Development
```bash
# Run tests
cd backend && bash ./scripts/test.sh

# Run specific test
cd backend && python -m pytest app/tests/api/routes/test_users.py::test_read_users -xvs

# Lint code
cd backend && bash ./scripts/lint.sh

# Format code
cd backend && bash ./scripts/format.sh

# Create migration
cd backend && alembic revision -m "migration_name" --autogenerate

# Apply migrations
cd backend && alembic upgrade head

# Database setup
cd backend && bash ./scripts/setup_db.sh
```

### Frontend Development
```bash
# Install dependencies
cd frontend && npm install

# Run development server
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Lint/format code
cd frontend && npm run lint

# Generate API client from OpenAPI
cd frontend && npm run generate-client

# Run E2E tests
cd frontend && npx playwright test

# Run specific test
cd frontend && npx playwright test tests/login.spec.ts
```

### Docker Development
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend

# Rebuild specific service
docker compose build backend

# Run backend tests in Docker
docker compose exec backend bash /app/scripts/test.sh

# Access database
docker compose exec db psql -U postgres app
```

## Architecture Patterns

### Backend Structure
- **Models**: SQLModel with UUID primary keys and timestamp mixins (`app/models/`)
- **Routes**: Modular route organization (`app/api/routes/`)
- **Auth**: JWT with refresh tokens, OAuth support (`app/api/routes/auth/`)
- **Config**: Pydantic Settings (`app/core/config.py`)
- **Database**: Async SQLAlchemy sessions (`app/db/session.py`)

### Frontend Structure
- **Routing**: File-based routing with TanStack Router (`src/routes/`)
- **API Client**: Auto-generated from OpenAPI (`src/client/`)
- **Auth**: Token management in localStorage (`src/hooks/useAuth.ts`)
- **Components**: Organized by feature (`src/components/`)
- **UI**: Chakra UI with custom theme (`src/theme.tsx`)

### Database Migrations
Alembic manages migrations. When modifying models:
1. Make changes to SQLModel classes
2. Generate migration: `alembic revision -m "description" --autogenerate`
3. Review generated migration file
4. Apply: `alembic upgrade head`

### Authentication Flow
- Login returns access and refresh tokens
- Access token expires in 15 minutes
- Refresh token used to get new access token
- Frontend automatically refreshes tokens

## Development URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB UI): http://localhost:8080
- MailCatcher: http://localhost:1080
- Traefik Dashboard: http://localhost:8090

## Environment Variables
Create `.env` file from template. Key variables:
- `POSTGRES_*`: Database connection
- `FIRST_SUPERUSER*`: Initial admin account
- `BACKEND_CORS_ORIGINS`: CORS configuration
- `SMTP_*`: Email settings
- `VITE_API_URL`: Frontend API endpoint