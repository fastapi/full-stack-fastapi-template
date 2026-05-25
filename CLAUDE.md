# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Full Stack FastAPI Template — a monorepo with a Python/FastAPI backend and a React/TypeScript frontend. Services run together via Docker Compose.

## Commands

### Full stack (Docker Compose)

```bash
docker compose watch          # start the full stack with live reload
docker compose logs backend   # tail logs for a specific service
```

### Backend (from `backend/`)

```bash
uv sync                       # install dependencies
source .venv/bin/activate     # activate virtual environment
fastapi dev app/main.py       # run dev server locally (without Docker)

# Testing
bash ./scripts/test.sh        # run tests with coverage
# Against running Docker stack:
docker compose exec backend bash scripts/tests-start.sh
docker compose exec backend bash scripts/tests-start.sh -x  # stop on first failure

# Linting / formatting
uv run prek run --all-files   # run all pre-commit hooks manually

# Database migrations (inside backend container)
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend (from `frontend/`)

```bash
bun install
bun run dev                   # dev server at http://localhost:5173
bun run build                 # type-check + production build
bun run lint                  # biome check + auto-fix
bun run generate-client       # regenerate OpenAPI client from openapi.json
bunx playwright test          # E2E tests (requires backend stack running)
bunx playwright test --ui     # E2E tests with UI
```

### Regenerate frontend API client

Run from project root after backend schema changes:

```bash
bash ./scripts/generate-client.sh
```

This exports the OpenAPI schema from the running backend, writes it to `frontend/openapi.json`, regenerates `frontend/src/client/`, and lints.

## Architecture

### Backend (`backend/`)

- **FastAPI** app entrypoint: `backend/app/main.py`
- **API routes**: `backend/app/api/routes/` — `login.py`, `users.py`, `items.py`, `utils.py`, `private.py` (local-only)
- **Models**: `backend/app/models.py` — all SQLModel models live here. Each model follows the pattern: `*Base` (shared) → `*Create`/`*Update` (input) → `*(table=True)` (DB) → `*Public` (API response)
- **CRUD**: `backend/app/crud.py` — database operations
- **Config**: `backend/app/core/config.py` — `Settings` loaded from `../.env` via pydantic-settings
- **DB setup**: `backend/app/core/db.py`
- **Auth**: `backend/app/core/security.py` + `backend/app/api/deps.py` — JWT via PyJWT, passwords via pwdlib (argon2/bcrypt)
- **Migrations**: Alembic in `backend/app/alembic/`; run inside the container

### Frontend (`frontend/src/`)

- **Router**: TanStack Router with file-based routes in `src/routes/`; `routeTree.gen.ts` is auto-generated
- **Data fetching**: TanStack Query wrapping the generated OpenAPI client in `src/client/`
- **UI components**: shadcn/ui (Radix UI primitives + Tailwind CSS v4) in `src/components/`
- **Forms**: react-hook-form + Zod validation
- **Theme**: next-themes for dark mode

### Key data flows

1. Backend models defined in `models.py` → Alembic generates migrations → FastAPI exposes OpenAPI schema
2. `scripts/generate-client.sh` exports the schema → `@hey-api/openapi-ts` generates typed client in `frontend/src/client/`
3. Frontend components import from `src/client/` and call API via TanStack Query hooks

### Environment

All configuration lives in the root `.env` file, which is read by both Docker Compose and the backend (`config.py` looks for `../.env`). The frontend reads `VITE_API_URL` from `frontend/.env`.

### Pre-commit hooks

Configured via `.pre-commit-config.yaml` using `prek`. Runs ruff (lint + format) on Python and Biome on TypeScript. Install with `uv run prek install -f` from `backend/`.
