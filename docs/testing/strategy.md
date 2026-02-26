---
title: "Testing Strategy"
doc-type: reference
status: draft
last-updated: 2026-02-26
updated-by: "initialise skill"
related-code:
  - "backend/tests/**/*"
  - "frontend/tests/**/*.spec.ts"
  - "backend/pyproject.toml"
  - "frontend/playwright.config.ts"
related-docs:
  - docs/testing/test-registry.md
  - docs/architecture/overview.md
tags: [testing, strategy, quality]
---

# Testing Strategy

## Overview

This project uses a split testing approach: Pytest for backend unit and integration tests, and Playwright for frontend end-to-end tests. The backend prioritizes unit and integration coverage while the frontend currently focuses on E2E workflows.

**Backend Framework:** Pytest <8.0.0
**Frontend E2E Framework:** Playwright 1.58.2
**Coverage Target:** Backend source coverage tracked via `coverage` package

## Testing Pyramid

| Level | Proportion | Framework | Purpose |
|-------|-----------|-----------|---------|
| Unit | 70% | Pytest | Individual functions, CRUD operations, utilities |
| Integration | 20% | Pytest | API endpoints with database, service interactions |
| E2E | 10% | Playwright | Critical user workflows (login, CRUD, settings) |

## Commands

### Backend

| Command | Purpose |
|---------|---------|
| `bash ./scripts/test.sh` | Run all backend tests (from project root) |
| `docker compose exec backend bash scripts/tests-start.sh` | Run tests in Docker |
| `docker compose exec backend bash scripts/tests-start.sh -x` | Stop on first error |
| `uv run pytest backend/tests/path/to/test.py` | Run single test file |
| `uv run coverage report` | View coverage report |

### Frontend

| Command | Purpose |
|---------|---------|
| `bunx playwright test` | Run all E2E tests |
| `bunx playwright test --ui` | Run tests with UI mode |
| `bunx playwright test tests/login.spec.ts` | Run single test file |
| `bun run test` | Run tests from project root |

## Test File Conventions

### Backend

| Convention | Pattern | Example |
|------------|---------|---------|
| Location | Separate `tests/` directory | `backend/tests/api/routes/test_users.py` |
| Naming | `test_*.py` | `test_users.py`, `test_items.py` |
| Structure | Function-based with fixtures | `def test_create_user(client, db):` |
| Subdirs | Mirror app structure | `tests/api/routes/`, `tests/crud/`, `tests/scripts/` |

### Frontend

| Convention | Pattern | Example |
|------------|---------|---------|
| Location | Separate `tests/` directory | `frontend/tests/login.spec.ts` |
| Naming | `*.spec.ts` | `admin.spec.ts`, `items.spec.ts` |
| Structure | Playwright test/expect | `test("description", async ({ page }) => {})` |
| Auth setup | Setup project dependency | `tests/auth.setup.ts` with storageState |

## Mocking

### Backend

| Type | Pattern | When to Use |
|------|---------|-------------|
| Database | pytest fixtures with test DB | All DB-dependent tests |
| HTTP | httpx / pytest-mock | External API calls |
| Config | Pydantic settings override via `patch` | Environment-specific tests |
| External services | `unittest.mock.patch` | SMTP, Sentry |

### Frontend

| Type | Pattern | When to Use |
|------|---------|-------------|
| Auth state | Playwright storageState | Tests requiring logged-in user |
| API | Running Docker backend | Full integration with real API |
| Users | Private API (`/api/v1/private/users/`) | Create test users via API |

## Coverage Configuration

### Backend (pyproject.toml)

| Metric | Configuration |
|--------|---------------|
| Source | `app` directory |
| Dynamic context | `test_function` |
| Report | `show_missing = true`, sorted by `-Cover` |
| HTML | `show_contexts = true` |

### Frontend

| Metric | Configuration |
|--------|---------------|
| Reporter | `html` (local) / `blob` (CI) |
| Trace | On first retry |
| Browsers | Chromium only (Firefox/WebKit available but disabled) |

## Test Fixtures (Backend)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `db` | session | Database session with init_db + cleanup |
| `client` | module | FastAPI TestClient instance |
| `superuser_token_headers` | module | Auth headers for superuser |
| `normal_user_token_headers` | module | Auth headers for regular user |

## Related

- [Test Registry](./test-registry.md)
- [Architecture Overview](../architecture/overview.md)
