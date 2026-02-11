# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Kila is the main full-stack web application for the GEO (Generative Engine Optimization) platform. It's based on tiangolo's Full Stack FastAPI Template and consists of a Python FastAPI backend and a React TypeScript frontend, orchestrated with Docker Compose.

## Build and Development Commands

### Backend (Python 3.10, uv, FastAPI)

```bash
cd backend
uv sync                                                    # install dependencies
ENVIRONMENT=development uvicorn app.main:app --reload      # run locally (port 8000)
fastapi dev app/main.py                                    # alternative local run
bash scripts/test.sh                                       # run all tests (pytest + coverage)
uv run ruff check . && uv run ruff format .                # lint + format
uv run mypy .                                              # type check
uv run prek install -f                                     # install pre-commit hooks
uv run prek run --all-files                                # run all pre-commit hooks manually
```

### Frontend (Node 24, pnpm, Vite 7, React 19)

```bash
cd frontend
pnpm install                  # install dependencies (or: make setup)
pnpm dev                      # dev server (port 5173)
pnpm build                    # production build (tsc + vite)
pnpm lint                     # biome check --write
npx playwright test           # E2E tests
pnpm generate-client          # regenerate OpenAPI TypeScript client from backend schema
```

### Docker Compose (full stack)

```bash
docker compose watch          # start all services with live reload
docker compose logs backend   # view specific service logs
docker compose stop frontend  # stop one service to run it locally instead
```

Development URLs:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Adminer (DB admin): http://localhost:8080
- Traefik dashboard: http://localhost:8090

### Alembic Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"   # create new migration
alembic upgrade head                                # apply all migrations
alembic downgrade -1                                # rollback one migration
```

Note: The Alembic env.py imports from `app.models` (SQLModel) and `app.core.config` for the database URL. Existing migrations are in `backend/app/alembic/versions/`.

## Architecture

### Backend Structure

- `app/main.py` — FastAPI app entry point with lifespan (DB init on startup), CORS, route mounting
- `app/api/main.py` — Router aggregation: mounts `auth`, `user_prompts`, and conditionally `debug` routes
- `app/api/routes/auth.py` — `/api/v1/auth` — signup/login with JWT (bcrypt password hashing, access + refresh tokens)
- `app/api/routes/user_prompts.py` — `/api/v1/prompts` — CRUD for brand prompts, alternative prompt generation via local AI
- `app/api/routes/brand_metrics.py` — `/api/v1/brand-metrics` — visibility, ranking, and brand score queries with time aggregation
- `app/core/db.py` — Async SQLAlchemy engine, session factory, `get_db` dependency, `init_db`
- `app/core/security.py` — (from template, may overlap with `utils/auth.py`)
- `app/utils/auth.py` — Password hashing (bcrypt/passlib), JWT creation/verification (python-jose)
- `app/services/local_ai_services.py` — `LocalModelService` for Ollama (local LLM, default: `qwen3-coder:30b`)
- `app/config/` — Environment-based config: `BaseConfig` → `DevelopmentConfig`/`BetaConfig`/`ProductionConfig`, loaded via `ENVIRONMENT` env var

### Config System

Settings are loaded from environment-specific `.env` files (`.env.development`, `.env.beta`, `.env.prod`) based on the `ENVIRONMENT` env var. Config classes inherit from `BaseConfig` in `app/config/base.py` and override specific values. The settings singleton is exported from `app/config/__init__.py`.

### Database

MySQL (`kila_intelligence`) via async SQLAlchemy + aiomysql. The backend uses `kila-models` package for shared table definitions (installed as `kila-models>=0.1.0` in pyproject.toml). Some models are also defined locally in `app/core/db.py` (BrandPromptTable).

### Auth

JWT-based (HS256). Signup creates user with nanoid, returns access + refresh tokens. Login verifies bcrypt hash, returns tokens. Tokens contain `sub` (user_id) and `email`.

### Frontend Structure

- `src/routes/` — TanStack Router file-based routing (`__root.tsx`, `app.tsx`, `app.dashboard.*`, `app.projects.tsx`, `app.users.tsx`)
- `src/components/app/` — App shell and feature components (AppLayout, dashboard, Projects, UserManagement)
- `src/components/landing/` — Public pages (LandingPage, Hero, AuthDialog, Pricing, etc.)
- `src/components/ui/` — shadcn/ui primitives (button, card, dialog, form, table, etc.)
- `src/clients/auth.ts` — Auth API client
- `src/routeTree.gen.ts` — Auto-generated route tree (do not edit manually)

Stack: React 19, TanStack Router + Query + Table, Tailwind CSS 4, shadcn/ui (Radix), Recharts, Zod, React Hook Form.

### Pre-commit Hooks (prek)

Defined in `.pre-commit-config.yaml`:
1. Standard checks: large files, TOML/YAML validation, trailing whitespace, end-of-file
2. `biome check` on frontend files
3. `ruff check --fix` and `ruff format` on Python files

### Ruff Configuration

Target: Python 3.10. Rules: E, W, F, I (isort), B (bugbear), C4, UP (pyupgrade), ARG001, T201 (no print). Excludes: alembic directory. Line length not enforced (E501 ignored).
