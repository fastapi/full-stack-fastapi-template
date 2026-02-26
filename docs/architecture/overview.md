---
title: "Aygentic Starter Template - Architecture Overview"
doc-type: reference
status: active
last-updated: 2026-02-26
updated-by: "initialise skill"
related-code:
  - backend/app/main.py
  - backend/app/api/main.py
  - backend/app/api/deps.py
  - backend/app/api/routes/
  - backend/app/core/config.py
  - backend/app/core/db.py
  - backend/app/core/security.py
  - backend/app/models.py
  - backend/app/crud.py
  - backend/app/alembic/
  - backend/scripts/prestart.sh
  - frontend/src/main.tsx
  - frontend/src/routes/
  - frontend/src/client/
  - frontend/src/components/
  - compose.yml
  - compose.override.yml
related-docs:
  - docs/architecture/decisions/
  - docs/api/overview.md
  - docs/data/models.md
tags: [architecture, system-design, full-stack, fastapi, react]
---

# Architecture Overview

## Purpose

The Aygentic Starter Template is a full-stack monorepo providing a production-ready foundation for building web applications. It combines a Python/FastAPI REST API backend with a React/TypeScript single-page application frontend, backed by PostgreSQL, and deployed via Docker Compose with Traefik as a reverse proxy. The system delivers JWT-based authentication, user management with role-based access control (regular users and superusers), CRUD operations for domain entities (users and items), email-based password recovery, and an auto-generated type-safe API client that bridges backend and frontend.

## System Context

```mermaid
C4Context
    title System Context Diagram

    Person(user, "End User", "Interacts with the application via browser")
    Person(admin, "Admin / Superuser", "Manages users and system configuration")

    System(system, "Aygentic Starter Template", "Full-stack web application with auth, CRUD, and admin capabilities")

    System_Ext(smtp, "SMTP Server", "Sends transactional emails: password reset, account creation, test emails")
    System_Ext(sentry, "Sentry", "Error monitoring and performance tracing (non-local environments only)")
    SystemDb_Ext(postgres, "PostgreSQL 18", "Persistent data storage for users and items")

    Rel(user, system, "Uses", "HTTPS")
    Rel(admin, system, "Administers", "HTTPS")
    Rel(system, smtp, "Sends emails via", "SMTP/TLS port 587")
    Rel(system, sentry, "Reports errors to", "HTTPS DSN")
    Rel(system, postgres, "Reads/writes data", "psycopg3 (postgresql+psycopg)")
```

## Key Components

| Component | Purpose | Technology | Location |
|-----------|---------|------------|----------|
| FastAPI Backend | REST API server handling auth, CRUD, and business logic | Python 3.10+, FastAPI >=0.114.2, Pydantic 2.x | `backend/app/main.py` |
| API Router | Mounts versioned route modules under `/api/v1` | FastAPI APIRouter | `backend/app/api/main.py` |
| Auth & Dependencies | JWT token validation, DB session injection, role-based guards | PyJWT, OAuth2PasswordBearer, Annotated Depends | `backend/app/api/deps.py` |
| Security Module | Password hashing (Argon2 primary + Bcrypt fallback) and JWT token creation | pwdlib (Argon2Hasher, BcryptHasher), PyJWT (HS256) | `backend/app/core/security.py` |
| Configuration | Environment-based settings with validation and secret enforcement | pydantic-settings, `.env` file, computed fields | `backend/app/core/config.py` |
| Database Engine | SQLAlchemy engine creation and initial superuser seeding | SQLModel, psycopg3 (postgresql+psycopg) | `backend/app/core/db.py` |
| Domain Models | SQLModel ORM tables + Pydantic request/response schemas | SQLModel (User, Item + 12 variant schemas) | `backend/app/models.py` |
| CRUD Utilities | Data access functions with timing-attack-safe authentication | SQLModel Session, Argon2 dummy hash comparison | `backend/app/crud.py` |
| Database Migrations | Schema version control and migration management | Alembic | `backend/app/alembic/` |
| Login Routes | OAuth2 token login, token test, password recovery/reset | FastAPI router | `backend/app/api/routes/login.py` |
| Users Routes | User CRUD, self-registration (`/signup`), profile management | FastAPI router | `backend/app/api/routes/users.py` |
| Items Routes | Item CRUD with ownership enforcement (superusers see all) | FastAPI router | `backend/app/api/routes/items.py` |
| Utils Routes | Health check endpoint, test email sending (superuser only) | FastAPI router | `backend/app/api/routes/utils.py` |
| Private Routes | Local-only user creation (gated by `ENVIRONMENT=local`) | FastAPI router | `backend/app/api/routes/private.py` |
| React Frontend | Single-page application with authenticated dashboard UI | React 19.1, TypeScript 5.9, Vite 7.3 (SWC) | `frontend/src/main.tsx` |
| Frontend Router | File-based routing with layout guards and code splitting | TanStack Router 1.157+ | `frontend/src/routes/` |
| Server State Management | API data fetching, caching, and global 401/403 error handling | TanStack Query 5.90+ (QueryCache, MutationCache) | `frontend/src/main.tsx` |
| Auto-generated API Client | Type-safe HTTP client generated from OpenAPI schema | @hey-api/openapi-ts, Axios 1.13 | `frontend/src/client/` |
| UI Component Library | Styled component system with dark theme support | Tailwind CSS 4.2, shadcn/ui (new-york variant) | `frontend/src/components/` |
| Reverse Proxy (Production) | TLS termination via Let's Encrypt, host-based routing, HTTPS redirect | Traefik 3.6 | `compose.yml` (labels) |
| Reverse Proxy (Local Dev) | HTTP-only proxy with insecure dashboard, no TLS | Traefik 3.6 | `compose.override.yml` |
| Database Admin | Web-based database inspection tool (pepa-linha-dark theme) | Adminer | `compose.yml` |
| Mail Catcher (Dev) | Local SMTP trap for development email testing | schickling/mailcatcher (ports 1025/1080) | `compose.override.yml` |
| Prestart Service | Waits for DB, runs Alembic migrations, seeds initial superuser | Bash, Alembic, Python | `backend/scripts/prestart.sh` |
| Playwright Runner | Containerised E2E test execution against backend | Playwright, Docker | `compose.override.yml` |

## Data Flow

### Authentication Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Frontend
    participant Backend
    participant Database

    Browser->>Frontend: Navigate to /login
    Frontend->>Backend: POST /api/v1/login/access-token (OAuth2PasswordRequestForm)
    Backend->>Database: SELECT user WHERE email = form.username
    alt User exists
        Database-->>Backend: User record (with hashed_password)
        Backend->>Backend: verify_password(plain, hashed) via pwdlib
        Note over Backend: Argon2 primary, Bcrypt fallback<br/>Auto-rehash if algorithm upgraded
    else User not found
        Database-->>Backend: None
        Backend->>Backend: verify_password(plain, DUMMY_HASH) for timing safety
        Backend-->>Frontend: 400 Incorrect email or password
    end
    alt Password verified
        Backend->>Backend: Check user.is_active
        Backend->>Backend: create_access_token(user.id, 8-day expiry)
        Note over Backend: JWT HS256 signed with SECRET_KEY<br/>Payload: {sub: user_id, exp: timestamp}
        Backend-->>Frontend: { access_token, token_type: "bearer" }
        Frontend->>Frontend: localStorage.setItem("access_token", token)
        Frontend-->>Browser: Redirect to dashboard (/)
    else Password invalid
        Backend-->>Frontend: 400 Incorrect email or password
    end
```

### Authenticated API Request Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Frontend
    participant TanStackQuery as TanStack Query
    participant APIClient as API Client (Axios)
    participant Backend
    participant Dependencies as FastAPI Deps
    participant Database

    Browser->>Frontend: User action (e.g., view items)
    Frontend->>TanStackQuery: useQuery({ queryKey, queryFn })
    TanStackQuery->>APIClient: Execute queryFn
    Note over APIClient: OpenAPI.TOKEN callback reads<br/>localStorage("access_token")
    APIClient->>Backend: GET /api/v1/items/ (Authorization: Bearer <token>)
    Backend->>Dependencies: OAuth2PasswordBearer extracts token
    Dependencies->>Dependencies: jwt.decode(token, SECRET_KEY, HS256)
    Dependencies->>Dependencies: Validate TokenPayload(sub=user_id)
    Dependencies->>Database: session.get(User, token_data.sub)
    Database-->>Dependencies: User record
    Dependencies->>Dependencies: Check user.is_active
    Dependencies-->>Backend: CurrentUser injected
    Backend->>Database: Query items (superuser=all, regular=owned)
    Database-->>Backend: Item records
    Backend-->>APIClient: JSON response (ItemsPublic: {data, count})
    APIClient-->>TanStackQuery: Response data
    TanStackQuery-->>Frontend: Cached data + loading/error state
    Frontend-->>Browser: Rendered UI

    Note over TanStackQuery,Frontend: QueryCache.onError + MutationCache.onError:<br/>On 401/403 ApiError -> clear token, redirect /login
```

## Deployment Architecture

### Docker Compose Services

The application runs as a set of Docker Compose services with two configuration layers:

**Production** (`compose.yml`):
- `db` -- PostgreSQL 18 with health check, persistent volume (`app-db-data`), env-based credentials
- `prestart` -- Runs `scripts/prestart.sh` (wait for DB, `alembic upgrade head`, seed superuser), exits on completion
- `backend` -- FastAPI server on port 8000, depends on healthy `db` + completed `prestart`, health check at `/api/v1/utils/health-check/`
- `frontend` -- Nginx-served SPA on port 80, built with `VITE_API_URL=https://api.${DOMAIN}`
- `adminer` -- Database admin UI on port 8080
- Traefik labels route `api.${DOMAIN}` to backend, `dashboard.${DOMAIN}` to frontend, `adminer.${DOMAIN}` to Adminer, all with HTTPS (Let's Encrypt `certresolver=le`)

**Local Development** (`compose.override.yml` extends `compose.yml`):
- `proxy` -- Traefik 3.6 with insecure dashboard (port 8090), no TLS, HTTP-only entrypoints
- `backend` -- Hot-reload via `fastapi run --reload`, `docker compose watch` for file sync, port 8000 exposed
- `frontend` -- Built with `VITE_API_URL=http://localhost:8000`, port 5173 exposed
- `mailcatcher` -- Local SMTP trap (SMTP port 1025, web UI port 1080) for email testing
- `playwright` -- Containerised E2E test runner with blob-report volume mount
- `traefik-public` network set to `external: false` for local operation

### Networking

```
Browser --> :80/:443 (Traefik)
               |
        Host-based routing:
               |
    api.${DOMAIN} --> backend:8000
    dashboard.${DOMAIN} --> frontend:80
    adminer.${DOMAIN} --> adminer:8080
               |
    backend --> db:5432 (internal network)
```

## Model Architecture

The domain models follow a layered schema pattern using SQLModel:

```
ModelBase (shared validated fields)
  |-- ModelCreate (input for creation, includes password)
  |-- ModelUpdate (partial input for updates, all optional)
  |-- Model(table=True) (ORM table with id, hashed_password, created_at, relationships)
  |-- ModelPublic (API response shape with id, no password)
  |-- ModelsPublic (paginated list response: {data: [], count: int})
```

**Entities:**
- **User** -- `id` (UUID), `email` (unique, indexed), `hashed_password`, `is_active`, `is_superuser`, `full_name`, `created_at` (UTC). Has cascade-delete relationship to Items.
- **Item** -- `id` (UUID), `title`, `description`, `created_at` (UTC), `owner_id` (FK to User with CASCADE delete).

**Additional schemas:** `UserRegister` (public signup), `UserUpdateMe` (self-service profile), `UpdatePassword` (current + new password), `Token` / `TokenPayload` (JWT), `NewPassword` (reset flow), `Message` (generic response).

## Security Architecture

### Password Hashing
- **Primary hasher:** Argon2id via `pwdlib.hashers.argon2.Argon2Hasher`
- **Fallback hasher:** Bcrypt via `pwdlib.hashers.bcrypt.BcryptHasher`
- **Auto-upgrade:** `verify_and_update()` returns a new hash if the stored hash uses an outdated algorithm, enabling transparent migration from Bcrypt to Argon2
- **Timing-attack prevention:** When a login attempt targets a non-existent email, `crud.authenticate()` still runs `verify_password()` against a precomputed `DUMMY_HASH` to ensure constant response time

### JWT Tokens
- **Algorithm:** HS256 (symmetric, signed with `SECRET_KEY`)
- **Payload:** `{"sub": "<user_uuid>", "exp": <utc_timestamp>}`
- **Expiry:** 8 days (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`, default 11520)
- **Validation:** `jwt.decode()` in `get_current_user` dependency, followed by DB lookup and `is_active` check
- **Storage:** Frontend stores token in `localStorage`, attached via `OpenAPI.TOKEN` callback on every Axios request

### Secret Enforcement
- `Settings._check_default_secret()` raises `ValueError` in staging/production if `SECRET_KEY`, `POSTGRES_PASSWORD`, or `FIRST_SUPERUSER_PASSWORD` are left as `"changethis"`
- In local environment, the same check emits a warning instead

### CORS
- `BACKEND_CORS_ORIGINS` parsed from comma-separated string or JSON array
- `FRONTEND_HOST` is always appended to allowed origins
- Middleware configured with `allow_credentials=True`, wildcard methods and headers

### Role-Based Access
- **Regular users:** Can manage own profile, own items, self-register via `/signup`
- **Superusers:** Full CRUD on all users and items, access to test-email endpoint, password recovery HTML preview
- Guard implemented as `get_current_active_superuser` dependency (raises 403 if `user.is_superuser` is False)

## Frontend Architecture

### Routing Structure (TanStack Router, file-based)

```
frontend/src/routes/
  __root.tsx          -- Root layout (wraps all routes)
  login.tsx           -- /login (public)
  signup.tsx          -- /signup (public)
  recover-password.tsx -- /recover-password (public)
  reset-password.tsx  -- /reset-password (public)
  _layout.tsx         -- Authenticated layout wrapper (auth guard)
  _layout/
    index.tsx         -- / (dashboard, requires auth)
    items.tsx         -- /items (items CRUD, requires auth)
    settings.tsx      -- /settings (user profile, requires auth)
    admin.tsx         -- /admin (user management, requires auth + superuser)
```

### State Management
- **Server state:** TanStack Query with global `QueryClient` configured with `QueryCache` and `MutationCache` error handlers that intercept 401/403 `ApiError` responses to clear the token and redirect to `/login`
- **Auth state:** `access_token` in `localStorage`, read via `OpenAPI.TOKEN` async callback
- **Theme:** `ThemeProvider` with dark mode default, persisted to `localStorage` under key `vite-ui-theme`
- **Notifications:** Sonner toast library with `richColors` and `closeButton` enabled

### API Client Generation
- Generated from the backend's OpenAPI schema at `/api/v1/openapi.json` using `@hey-api/openapi-ts`
- Output written to `frontend/src/client/` (auto-generated, must not be manually edited)
- Transport layer: Axios 1.13
- Regeneration: `bash ./scripts/generate-client.sh` (also triggered by pre-commit hook on backend changes)

## Architecture Decisions

Key decisions are documented as ADRs in `docs/architecture/decisions/`:

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| - | No ADRs recorded yet | - | - |

<!-- TODO: Populate as architectural decisions are documented -->

## Known Constraints

1. **Single-database architecture** -- The system uses a single PostgreSQL 18 instance for all data. This simplifies operations but limits read/write scaling to vertical scaling unless read replicas are introduced.

2. **Stateless JWT with no revocation** -- Access tokens (8-day expiry) cannot be individually revoked once issued. The only mechanism for invalidation is changing the `SECRET_KEY`, which invalidates all tokens simultaneously. Per-session revocation would require a token blacklist or a switch to shorter-lived tokens with refresh tokens.

3. **localStorage token storage** -- JWT tokens are stored in `localStorage`, which is accessible to any JavaScript running on the same origin. This trades security (compared to httpOnly cookies) for simplicity in the SPA architecture. XSS vulnerabilities would expose tokens.

4. **Monorepo coupling** -- Backend and frontend share a single repository and Docker Compose deployment. While this simplifies development coordination, it means both must be deployed together and share the same release cadence.

5. **Auto-generated API client (build-time dependency)** -- The frontend API client is generated from the backend's OpenAPI schema via `@hey-api/openapi-ts`. Any backend API change requires regenerating the client (`scripts/generate-client.sh`) to maintain type safety. The pre-commit hook automates this, but it creates a build-time coupling.

6. **Environment-gated private routes** -- The `private` API router (unrestricted user creation) is only mounted when `ENVIRONMENT=local`. This is a configuration-based guard rather than an infrastructure-based one. Misconfigured environments could expose this endpoint.

7. **Default secrets in local development** -- `SECRET_KEY`, `POSTGRES_PASSWORD`, and `FIRST_SUPERUSER_PASSWORD` default to `"changethis"`. The `Settings` validator warns in local mode but raises `ValueError` in staging/production, preventing deployment with default credentials.

## Related Documents

- [API Documentation](../api/overview.md)
- [Data Models](../data/models.md)
- [Deployment Guide](../deployment/environments.md)
- [Testing Strategy](../testing/strategy.md)
