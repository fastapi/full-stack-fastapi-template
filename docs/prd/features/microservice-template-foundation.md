# PRD: Microservice Template Foundation

**Version**: 1.1
**Component**: Full-stack (Backend-primary)
**Status**: Draft
**Last Updated**: 2026-02-27
**Related**: N/A (foundational template — no predecessor PRDs)

---

## 1. Overview

### What & Why

Aygentic engineers waste hours re-implementing auth, error handling, logging, config, and database wiring every time they spin up a new microservice. This PRD defines the transformation of the existing full-stack FastAPI + React template into an **opinionated, reusable microservice starter** that encodes Aygentic platform conventions. The goal: clone, set three env vars, and have a production-grade service running in under 10 minutes.

### Scope

- **In scope**:
  - Replace PostgreSQL + SQLAlchemy/SQLModel with **Supabase** (supabase-py REST client, one Supabase project per service)
  - Strip all app-specific features (users, passwords, login flows, email recovery, items)
  - Retain only: operational endpoints (`/healthz`, `/readyz`, `/version`) + one sample **Entity** CRUD resource
  - Add **WITH_UI** toggle: copier.yml template variable + runtime env var — `false` = backend-only, `true` = backend + frontend
  - Backend runs fully standalone — zero references to frontend artifacts
  - **Clerk JWT verification** middleware (validates Bearer token, extracts principal: user ID, roles, org)
  - Full suite of **standardised service conventions** (see Section 4)
  - All tests updated for new stack (Supabase, Clerk, Entity)
  - Docker Compose adjusted for WITH_UI flag
  - GitHub Actions CI adjusted for WITH_UI flag
  - **Gateway-ready conventions** — standardised path prefixes, health endpoints, service metadata, and correlation ID propagation that make services routable through any API gateway. Includes reference Traefik configuration.
  - **Platform-agnostic deployment guidance** — containerised deployment conventions with GHCR, GitHub Actions CI/CD, and environment promotion (staging → production). No platform lock-in; works with any container host (Alibaba Cloud, Railway, Cloud Run, Fly.io, self-hosted).

- **Out of scope**:
  - User management service (separate repo)
  - Multi-tenancy / workspace isolation
  - Service mesh, Kubernetes, Terraform
  - Shared NPM/PyPI packages
  - Full API gateway implementation (template is gateway-ready, not gateway-inclusive)
  - Platform-specific deployment automation (template provides generic container workflows)
  - Multi-region / disaster recovery

### Living Document

This PRD is a living document that will evolve during development:
- Update as implementation reveals better patterns
- Document learnings from Supabase/Clerk integration
- Track scope changes with justification
- Version with dates when major changes occur

### Non-Functional Requirements

- **Performance**: Health endpoints respond in <50ms; Entity CRUD <200ms at p95
- **Security**: All non-operational endpoints require valid Clerk JWT; secrets never logged; CORS locked to configured origins
- **Startup**: Cold start to first successful health check <5s (backend container)
- **Developer Experience**: Clone-to-running in <10 minutes with 3 env vars (SUPABASE_URL, SUPABASE_SERVICE_KEY, CLERK_SECRET_KEY)
- **Observability**: Structured JSON logs with request ID correlation on every request
- **Test Coverage**: 90% line coverage on backend (pytest); frontend coverage when WITH_UI=true
- **Deployment**: Containerised with platform-agnostic GitHub Actions. Staging auto-deploys on merge to main; production deploys on release publish. Zero-downtime deployments.
- **Time to Production**: From cloned template to live deployment in <30 minutes on any container platform (including Supabase project creation, Clerk application setup, and container host configuration)

---

## 2. User Stories

### US-1: Bootstrap a New Microservice
**As an** Aygentic engineer
**I want** to clone the template, set env vars, and run `docker compose up`
**So that** I have a production-grade microservice running in under 10 minutes with auth, logging, error handling, and a sample CRUD endpoint already wired.

### US-2: Backend-Only Service
**As an** Aygentic engineer building a headless API service
**I want** to set `WITH_UI=false` and have zero frontend artifacts, Docker services, or CI steps
**So that** my service stays lean with no dead code or unnecessary build steps.

### US-3: Full-Stack Service
**As an** Aygentic engineer building a service with a UI
**I want** to set `WITH_UI=true` and have the React frontend included, connected to the backend, and tested in CI
**So that** I get a complete full-stack development environment.

### US-4: Clerk Authentication
**As an** Aygentic engineer
**I want** incoming requests authenticated via Clerk JWT verification
**So that** I get a verified principal (user ID, roles, org) without implementing auth from scratch.

### US-5: Sample Entity CRUD
**As an** Aygentic engineer learning the template patterns
**I want** a complete Entity CRUD resource as a reference implementation
**So that** I can replicate the pattern when adding my own domain resources.

### US-6: Consistent Observability
**As an** Aygentic engineer debugging a production issue
**I want** structured JSON logs with request IDs, correlation fields, and standard error shapes
**So that** I can trace requests across services and aggregate logs in a centralised platform.

### US-7: Deploy to Production
**As an** Aygentic engineer
**I want** to merge to main for staging and publish a release for production
**So that** my service deploys with zero downtime via any container platform, with the exact same image promoted from staging to production.

### US-8: Multi-Service Communication
**As an** Aygentic engineer running multiple services from this template
**I want** services to communicate via HTTP with automatic correlation ID propagation
**So that** I can trace requests across services and debug distributed issues using a single correlation ID.

---

## 3. Acceptance Criteria (Gherkin)

### Scenario: Backend-only startup (WITH_UI=false)
```gherkin
Given the template is cloned and .env has WITH_UI=false
And SUPABASE_URL, SUPABASE_SERVICE_KEY, CLERK_SECRET_KEY are configured
When I run "docker compose up"
Then only backend and Supabase-related services start
And no frontend container is built or started
And no frontend files are referenced by the backend
And GET /healthz returns 200 with {"status": "ok"}
```

### Scenario: Full-stack startup (WITH_UI=true)
```gherkin
Given the template is cloned and .env has WITH_UI=true
When I run "docker compose up"
Then backend and frontend containers both start
And the frontend is accessible on its configured port
And the frontend can make authenticated API calls to the backend
```

### Scenario: Valid Clerk JWT grants access
```gherkin
Given a valid Clerk JWT in the Authorization header
When I call GET /api/v1/entities
Then the request succeeds with 200
And the response contains entity data
And the request log includes the authenticated user ID
```

### Scenario: Missing or invalid JWT returns 401
```gherkin
Given no Authorization header (or an expired/invalid JWT)
When I call GET /api/v1/entities
Then the response is 401
And the body matches {"error": "UNAUTHORIZED", "message": "<reason>", "code": "AUTH_INVALID_TOKEN", "request_id": "<uuid>"}
```

### Scenario: Entity CRUD lifecycle
```gherkin
Given I am authenticated with a valid Clerk JWT
When I POST /api/v1/entities with {"title": "Test Entity", "description": "A test"}
Then the response is 201 with the created entity including id, created_at, updated_at
When I GET /api/v1/entities/{id}
Then the response is 200 with the entity data
When I PATCH /api/v1/entities/{id} with {"title": "Updated Title"}
Then the response is 200 with the updated entity
When I DELETE /api/v1/entities/{id}
Then the response is 204
And GET /api/v1/entities/{id} returns 404
```

### Scenario: Operational endpoints require no auth
```gherkin
Given no Authorization header
When I call GET /healthz
Then the response is 200 with {"status": "ok"}
When I call GET /readyz
Then the response is 200 with {"status": "ready", "checks": {"supabase": "ok"}}
When I call GET /version
Then the response is 200 with {"version": "<semver>", "commit": "<sha>", "build_time": "<iso8601>", "environment": "<env>"}
```

### Scenario: Readiness check detects Supabase failure
```gherkin
Given Supabase is unreachable
When I call GET /readyz
Then the response is 503 with {"status": "not_ready", "checks": {"supabase": "error"}}
```

### Scenario: CI runs backend-only when WITH_UI=false
```gherkin
Given the CI workflow is triggered
And WITH_UI is false (or frontend files do not exist)
When the workflow executes
Then lint, type-check, and pytest steps run for backend
And no frontend lint, build, or Playwright steps run
And the pipeline passes
```

### Scenario: CI runs full stack when WITH_UI=true
```gherkin
Given the CI workflow is triggered
And WITH_UI is true
When the workflow executes
Then backend lint, type-check, and pytest steps run
And frontend lint, type-check, build, and Playwright E2E steps run
And the pipeline passes
```

### Scenario: Deploy to staging on merge to main
```gherkin
Given the CI pipeline passes on the main branch
When a commit is pushed to main
Then the GitHub Actions workflow builds the Docker image
And pushes it to GitHub Container Registry (GHCR) tagged with the commit SHA
And the pluggable deploy step deploys the image to the staging environment
And GET /healthz on staging returns 200
And GET /version on staging returns the correct commit SHA
```

### Scenario: Promote staging to production via release
```gherkin
Given a Docker image is deployed and validated on staging
When a GitHub release is published with tag v1.x.x
Then the existing staging image (tagged with commit SHA) is re-tagged as v1.x.x
And the pluggable deploy step deploys the v1.x.x image to the production environment
And the production image is identical to the staging image (no rebuild)
And GET /version on production returns the release version
```

### Scenario: Rollback production to previous version
```gherkin
Given production is running image v1.2.0 and an issue is detected
When the deploy workflow is triggered with the previous tag v1.1.0
Then the v1.1.0 image (still stored in GHCR) is deployed to production
And GET /version on production returns v1.1.0
And the rollback completes within 5 minutes
```

### Scenario: Service-to-service communication with correlation
```gherkin
Given Service A receives a request with X-Correlation-ID "trace-123"
When Service A calls Service B using the shared HTTP client
Then the request to Service B includes X-Correlation-ID "trace-123"
And both services log entries include correlation_id "trace-123"
And Service B's response is logged by Service A with duration and status
```

### Scenario: Gateway-ready service metadata
```gherkin
Given a service is deployed to any container platform
When I call GET /version without authentication
Then the response includes "service_name", "version", "commit", "build_time", "environment"
And the service exposes GET /healthz (liveness) and GET /readyz (readiness) without auth
And all API routes are prefixed with /api/v1
And the service can be placed behind any API gateway without modification
```

---

## 4. Functional Requirements

### 4.1 Standardised Service Conventions — Canonical List

Every service generated from this template MUST implement the following conventions. This is the exhaustive list that makes a service "feel like it belongs to the Aygentic platform."

#### 4.1.1 Operational Endpoints

| Endpoint | Purpose | Auth | Response |
|----------|---------|------|----------|
| `GET /healthz` | Liveness probe — process is alive | None | `{"status": "ok"}` → 200 |
| `GET /readyz` | Readiness probe — dependencies healthy | None | `{"status": "ready", "checks": {...}}` → 200 or 503 |
| `GET /version` | Build metadata | None | `{"version", "commit", "build_time", "environment"}` → 200 |

- `/healthz`: Returns 200 immediately. No dependency checks. Used by container orchestrators for liveness.
- `/readyz`: Checks Supabase connectivity (and any other registered dependencies). Returns 503 if any check fails. Used by load balancers / orchestrators for readiness.
- `/version`: Returns build-time metadata injected via env vars or build args. Fields: `version` (semver from pyproject.toml), `commit` (git SHA), `build_time` (ISO 8601), `environment` (local/staging/production).

#### 4.1.2 Unified Error Shape

Every error response from the API MUST use this JSON structure:

```json
{
  "error": "NOT_FOUND",
  "message": "Entity with id '550e8400-e29b-41d4-a716-446655440000' not found.",
  "code": "ENTITY_NOT_FOUND",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `error` | `string` | HTTP status category in UPPER_SNAKE_CASE (e.g., `BAD_REQUEST`, `UNAUTHORIZED`, `NOT_FOUND`, `INTERNAL_ERROR`) |
| `message` | `string` | Human-readable description of the error. Safe to display to end users. |
| `code` | `string` | Machine-readable error code in UPPER_SNAKE_CASE. Unique per error type (e.g., `AUTH_INVALID_TOKEN`, `ENTITY_NOT_FOUND`, `VALIDATION_FAILED`). |
| `request_id` | `string` | UUID of the request. Matches `X-Request-ID` response header. |

**Validation errors** (422) extend the shape with a `details` array:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "code": "VALIDATION_FAILED",
  "request_id": "...",
  "details": [
    {"field": "title", "message": "Field required", "type": "missing"}
  ]
}
```

**HTTP status code mapping**:

| Status | `error` value | When |
|--------|---------------|------|
| 400 | `BAD_REQUEST` | Malformed request body or params |
| 401 | `UNAUTHORIZED` | Missing, expired, or invalid JWT |
| 403 | `FORBIDDEN` | Valid JWT but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Duplicate or state conflict |
| 422 | `VALIDATION_ERROR` | Pydantic/Zod validation failure |
| 429 | `RATE_LIMITED` | Too many requests (future) |
| 500 | `INTERNAL_ERROR` | Unhandled server error |
| 503 | `SERVICE_UNAVAILABLE` | Dependency down (e.g., Supabase) |

**Implementation**: Global exception handlers registered on the FastAPI app that catch `HTTPException`, `RequestValidationError`, and unhandled `Exception`, formatting them into the standard shape. The `request_id` is injected from middleware.

#### 4.1.3 Configuration (Pydantic BaseSettings)

All configuration lives in a single `app/core/config.py` with a `Settings` class extending `pydantic_settings.BaseSettings`.

**Required env vars** (service won't start without these):

| Variable | Type | Description |
|----------|------|-------------|
| `SUPABASE_URL` | `AnyHttpUrl` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `SecretStr` | Supabase service role key (server-side only) |
| `CLERK_SECRET_KEY` | `SecretStr` | Clerk secret key for JWT verification |

**Optional env vars** (sensible defaults):

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENVIRONMENT` | `Literal["local", "staging", "production"]` | `"local"` | Deployment environment |
| `SERVICE_NAME` | `str` | `"my-service"` | Service identifier for logs/traces |
| `SERVICE_VERSION` | `str` | `"0.1.0"` | Semver from pyproject.toml |
| `LOG_LEVEL` | `Literal["DEBUG", "INFO", "WARNING", "ERROR"]` | `"INFO"` | Minimum log level |
| `LOG_FORMAT` | `Literal["json", "console"]` | `"json"` | Log output format (console = human-readable for local dev) |
| `API_V1_STR` | `str` | `"/api/v1"` | API version prefix |
| `BACKEND_CORS_ORIGINS` | `list[AnyHttpUrl]` | `[]` | Allowed CORS origins |
| `WITH_UI` | `bool` | `false` | Whether frontend is included (runtime awareness) |
| `CLERK_JWKS_URL` | `str` | Auto-derived from Clerk | JWKS endpoint override |
| `CLERK_AUTHORIZED_PARTIES` | `list[str]` | `[]` | Allowed `azp` claim values |
| `GIT_COMMIT` | `str` | `"unknown"` | Git SHA injected at build time |
| `BUILD_TIME` | `str` | `"unknown"` | ISO 8601 build timestamp |
| `HTTP_CLIENT_TIMEOUT` | `int` | `30` | Default httpx timeout (seconds) |
| `HTTP_CLIENT_MAX_RETRIES` | `int` | `3` | Default httpx retry count |
| `SENTRY_DSN` | `str \| None` | `None` | Sentry DSN (optional) |

**Validation rules**:
- In `production` environment: `SUPABASE_SERVICE_KEY` and `CLERK_SECRET_KEY` must not contain `"changethis"`.
- `BACKEND_CORS_ORIGINS` must not be wildcard (`*`) in production.
- Settings are frozen (immutable) after initialization.

#### 4.1.4 Structured Logging

**Library**: `structlog` configured for JSON output.

**Every log entry** includes these base fields:

| Field | Source | Example |
|-------|--------|---------|
| `timestamp` | Auto | `"2026-02-27T14:30:00.123Z"` |
| `level` | Logger | `"info"` |
| `event` | Logger | `"entity_created"` |
| `service` | Config | `"my-service"` |
| `version` | Config | `"0.1.0"` |
| `environment` | Config | `"production"` |
| `request_id` | Middleware | `"a1b2c3d4-..."` |
| `correlation_id` | Header | `"x9y8z7w6-..."` (from `X-Correlation-ID`, or same as request_id) |

**Request/response logs**: Every HTTP request is logged at `info` level with:
- `method`, `path`, `status_code`, `duration_ms`, `user_id` (if authenticated)

**Local development**: When `LOG_FORMAT=console`, output is human-readable colored text instead of JSON.

**Rules**:
- Never log secrets, tokens, passwords, or PII
- Log at `warning` for client errors (4xx), `error` for server errors (5xx)
- Log at `info` for successful operations
- Log at `debug` for detailed request/response payloads (local only)

#### 4.1.5 Request ID & Correlation

**Middleware** generates a UUID v4 `request_id` for every incoming request:
- Stored in request state, available to all handlers and dependencies
- Returned in `X-Request-ID` response header
- Included in every log entry and error response

**Correlation ID** (`X-Correlation-ID` header):
- If the incoming request includes `X-Correlation-ID`, propagate it
- If absent, use the `request_id` as the correlation ID
- Forward to all outgoing HTTP calls (via shared httpx client)

#### 4.1.6 HTTP Client (Service-to-Service)

**Shared `httpx.AsyncClient`** wrapper in `app/core/http_client.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| Timeout (connect) | 5s | TCP connection timeout |
| Timeout (read) | 30s | Response read timeout |
| Retries | 3 | Exponential backoff: 0.5s, 1s, 2s |
| Retry on | 502, 503, 504 | Gateway/service errors only |
| Circuit breaker | 5 failures / 60s | Opens circuit after threshold, half-open after 60s |
| Headers | `X-Request-ID`, `X-Correlation-ID` | Propagated from current request context |

**Usage**: Injected via FastAPI dependency. Not instantiated directly.

```python
async def call_other_service(http: HttpClientDep):
    response = await http.get("https://other-service/api/v1/resource")
```

#### 4.1.7 Database (Supabase)

**Client**: `supabase-py` (async client via `create_async_client` or sync via `create_client`).

**Lifecycle**:
- Client initialized at FastAPI `lifespan` startup
- Client stored in `app.state.supabase`
- Injected into route handlers via FastAPI dependency
- No explicit shutdown needed (HTTP-based, not connection-pool based)

**Operations**: All database operations go through the supabase-py client's table builder:

```python
# Create
response = supabase.table("entities").insert({"title": "...", "owner_id": user_id}).execute()

# Read (single)
response = supabase.table("entities").select("*").eq("id", entity_id).single().execute()

# Read (list with pagination)
response = supabase.table("entities").select("*", count="exact").range(offset, offset + limit - 1).execute()

# Update
response = supabase.table("entities").update({"title": "..."}).eq("id", entity_id).execute()

# Delete
response = supabase.table("entities").delete().eq("id", entity_id).execute()
```

**Migrations**: Supabase CLI native migrations (see Section 5 — Architecture Decision: Migrations).

**Row-Level Security (RLS)**: Enabled on all tables. Policies enforce that users can only access their own entities. The service role key bypasses RLS for admin operations.

#### 4.1.8 Authentication (Clerk JWT)

**Library**: `clerk-backend-api` (official Clerk Python SDK).

**Flow**:
1. Client sends `Authorization: Bearer <clerk_jwt>` header
2. FastAPI dependency extracts the token
3. `clerk.authenticate_request()` verifies the JWT against Clerk's JWKS endpoint (cached)
4. On success, extracts principal: `user_id` (sub claim), `org_id`, `roles`, `session_id`
5. On failure, raises 401 with standard error shape

**Principal model**:

```python
class Principal(BaseModel):
    user_id: str          # Clerk user ID (sub claim)
    org_id: str | None    # Organization ID (if using Clerk orgs)
    roles: list[str]      # User roles from session claims
    session_id: str       # Clerk session ID
```

**FastAPI dependency**:

```python
PrincipalDep = Annotated[Principal, Depends(get_current_principal)]
```

**Public routes**: `/healthz`, `/readyz`, `/version`, and any routes explicitly marked with `dependencies=[]` (no auth dependency).

**Configuration**: Clerk secret key and authorized parties via env vars. No hardcoded values.

#### 4.1.9 Request/Response Patterns

**Pagination** (list endpoints):
- Query params: `offset` (default 0), `limit` (default 20, max 100)
- Response: `{"data": [...], "count": <total>}`

**Response headers**:
- `X-Request-ID`: Request identifier (UUID v4)
- `Content-Type`: `application/json`
- Standard security headers (see 4.1.12)

**Request validation**: Pydantic models for all request bodies. Validation errors caught globally and formatted as standard error shape.

#### 4.1.10 API Versioning

- URL path prefix: `/api/v1`
- No header-based versioning
- When v2 is needed, add a new router at `/api/v2` — old routes stay

#### 4.1.11 Dependency Injection

All cross-cutting concerns are injected via `Annotated[T, Depends(...)]` types:

| Dependency | Type | Description |
|------------|------|-------------|
| `SupabaseDep` | `Client` | Supabase client instance |
| `PrincipalDep` | `Principal` | Authenticated user from Clerk JWT |
| `HttpClientDep` | `HttpClient` | Shared httpx wrapper |
| `RequestIdDep` | `str` | Current request ID |

All dependencies are overridable in tests via `app.dependency_overrides`.

#### 4.1.12 Security Headers

Applied via middleware on all responses:

| Header | Value |
|--------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `0` (disabled, CSP preferred) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (production only) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |

CORS configured from `BACKEND_CORS_ORIGINS` env var. No wildcard in production.

#### 4.1.13 Startup & Shutdown Lifecycle

**FastAPI lifespan** context manager:

1. **Startup**:
   - Validate settings (fail fast if required env vars missing)
   - Initialize Supabase client
   - Initialize structlog
   - Initialize Sentry (if DSN configured)
   - Log startup event with service name, version, environment

2. **Shutdown**:
   - Log shutdown event
   - Close httpx client pool
   - Flush Sentry

#### 4.1.14 Docker Conventions

**Dockerfile (backend)**:
- Multi-stage build: builder stage (install deps with `uv`) + runtime stage (copy installed packages)
- Base: `python:3.10-slim`
- Non-root user (`appuser`)
- Health check: Python-based (no `curl` in final image) — `CMD ["python", "-c", "import httpx; httpx.get('http://localhost:8000/healthz').raise_for_status()"]`
- Build args: `GIT_COMMIT`, `BUILD_TIME`
- Uses `uv` for dependency management
- OCI labels for GHCR metadata: `org.opencontainers.image.source`, `org.opencontainers.image.version`, `org.opencontainers.image.revision`

**Dockerfile (frontend)** — only when WITH_UI=true:
- Multi-stage: Bun build + Nginx runtime
- Build arg: `VITE_API_URL`

**compose.yml**:
- Backend service (always)
- Frontend service (conditional on WITH_UI via Docker Compose profiles)
- Traefik reverse proxy (always)

**Docker Compose profiles**:
```yaml
services:
  frontend:
    profiles: ["ui"]
    # ... only starts with: docker compose --profile ui up
```

When `WITH_UI=true`, the startup script (or developer) uses `docker compose --profile ui up`. When `WITH_UI=false`, plain `docker compose up` starts backend only.

#### 4.1.15 CI/CD Conventions

**Pipeline stages**: Lint → Type-check → Test → Build → Push → Deploy

**CI (on every PR and push to main)**:

**Backend** (always runs):
1. `ruff check` + `ruff format --check` (lint)
2. `mypy` (type check)
3. `pytest` with 90% coverage gate (test)
4. Docker image build (build)

**Frontend** (only when WITH_UI=true):
1. `biome check` (lint)
2. `tsc --noEmit` (type check)
3. `bun run build` (build)
4. `playwright test` (E2E)

**CD (deployment)** — see Section 4.1.19 for full details:

| Trigger | Pipeline | Target |
|---------|----------|--------|
| Push to `main` | CI → Build image → Push to GHCR → Deploy (pluggable) | Staging |
| Release published | Re-tag staging image → Deploy (pluggable) | Production |
| PR opened | CI only (platform PR preview optional) | PR preview |

**Gating logic**: CI workflow checks for existence of `frontend/` directory OR reads `WITH_UI` from `.env` / repository variable to decide whether to run frontend steps.

**Unified workflow**: A single `ci.yml` handles CI. Separate `deploy-staging.yml` and `deploy-production.yml` handle deployments with pluggable platform-specific deploy steps.

#### 4.1.16 Project Structure Convention

```
{service_name}/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app + lifespan
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Pydantic BaseSettings
│   │   │   ├── supabase.py          # Client init + dependency
│   │   │   ├── auth.py              # Clerk JWT verification + Principal
│   │   │   ├── errors.py            # Error models + global handlers
│   │   │   ├── logging.py           # structlog configuration
│   │   │   ├── http_client.py       # httpx wrapper
│   │   │   └── middleware.py        # Request ID, security headers, logging
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py              # Annotated dependency types
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py        # /healthz, /readyz, /version
│   │   │       └── entities.py      # Sample Entity CRUD
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── entity.py            # Entity request/response models
│   │   │   ├── auth.py              # Principal model
│   │   │   └── common.py            # Pagination, error shapes
│   │   └── services/
│   │       ├── __init__.py
│   │       └── entity_service.py    # Entity business logic + Supabase CRUD
│   ├── tests/
│   │   ├── conftest.py              # Fixtures: mock Supabase, mock Clerk
│   │   ├── unit/
│   │   │   ├── test_config.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_errors.py
│   │   │   └── test_entity_service.py
│   │   └── integration/
│   │       ├── test_health.py
│   │       └── test_entities.py
│   ├── Dockerfile
│   └── pyproject.toml
├── supabase/
│   ├── config.toml                  # Supabase local config
│   └── migrations/
│       └── 20260227000000_create_entities.sql
├── frontend/                        # Only when WITH_UI=true
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── ...
├── compose.yml
├── compose.override.yml
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Unified CI: backend always, frontend gated
│       ├── deploy-staging.yml       # GHCR build/push + pluggable staging deploy
│       └── deploy-production.yml    # Re-tag image + pluggable production deploy
├── copier.yml                       # Template configuration
├── pyproject.toml                   # Root project metadata
├── CLAUDE.md
└── README.md
```

#### 4.1.17 Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Python files | snake_case | `entity_service.py` |
| Python functions | snake_case | `get_entity_by_id()` |
| Python classes | PascalCase | `EntityCreate` |
| Pydantic models | `{Entity}{Action}` pattern | `EntityCreate`, `EntityUpdate`, `EntityPublic` |
| API routes | kebab-case (if multi-word) | `/api/v1/entities` |
| Env vars | UPPER_SNAKE_CASE | `SUPABASE_URL` |
| Error codes | UPPER_SNAKE_CASE | `ENTITY_NOT_FOUND` |
| DB tables | snake_case plural | `entities` |
| DB columns | snake_case | `created_at` |
| TS components | PascalCase | `EntityList.tsx` |
| TS utilities | camelCase | `formatDate.ts` |
| Docker services | kebab-case | `my-service-backend` |
| Git branches | type/STORY-ID-description | `feature/STORY-123-add-entities` |

#### 4.1.18 Pydantic Model Patterns

Follow the layered model pattern from the existing template, adapted for Supabase:

```python
# Base fields shared across create/update/read
class EntityBase(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)

# Fields needed to create
class EntityCreate(EntityBase):
    pass  # title is required from base

# Fields allowed in update (all optional)
class EntityUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)

# Full entity returned from API
class EntityPublic(EntityBase):
    id: UUID
    owner_id: str
    created_at: datetime
    updated_at: datetime

# List response
class EntitiesPublic(BaseModel):
    data: list[EntityPublic]
    count: int
```

#### 4.1.19 Deployment Conventions

**Approach**: Platform-agnostic containerised deployment. The template provides a production-ready Dockerfile, GHCR integration, and GitHub Actions workflows with a **pluggable deploy step**. Teams customise the deploy step for their chosen platform (Alibaba Cloud ECS/ACR, Railway, Cloud Run, Fly.io, self-hosted Docker Compose, etc.).

**Why platform-agnostic**: Since the template uses managed services (Supabase for database, Clerk for auth), the backend is a **stateless Docker container** with no local state to manage. Any platform that runs containers works. Locking to a specific platform would limit reusability across teams deploying to different cloud providers.

**Environment model**:

| Environment | Trigger | Purpose |
|-------------|---------|---------|
| Local | `docker compose up` | Development with hot-reload |
| Staging | Push to `main` branch | Pre-production validation |
| Production | GitHub release published | Live traffic |
| PR Preview | Pull request opened (optional) | Per-PR isolated environment |

**Container registry**: GitHub Container Registry (GHCR) as default.

| Step | Action |
|------|--------|
| Build | `docker build` in GitHub Actions |
| Tag (staging) | `ghcr.io/{org}/{service}:{sha}` |
| Tag (production) | Re-tag staging image as `ghcr.io/{org}/{service}:v{semver}` |
| Tag (latest) | `ghcr.io/{org}/{service}:latest` updated on production deploy |

**Required environment secrets** (set per environment on the container platform):

| Secret | Description | Per-Environment |
|--------|-------------|-----------------|
| `SUPABASE_URL` | Supabase project URL | Yes — separate Supabase project per env |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Yes |
| `CLERK_SECRET_KEY` | Clerk secret key | Yes — separate Clerk application per env |
| `ENVIRONMENT` | `staging` or `production` | Yes |
| `SERVICE_NAME` | Service identifier for logs/traces | No — same across envs |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | Yes — env-specific frontend URLs |
| `SENTRY_DSN` | Sentry DSN (optional) | Yes — separate Sentry project per env |

**Required GitHub Actions secrets**:

| Secret | Description |
|--------|-------------|
| `GHCR_TOKEN` | GitHub token with `write:packages` scope (or use `GITHUB_TOKEN`) |
| Platform-specific deploy token | e.g., `RAILWAY_TOKEN`, `ALIBABA_ACCESS_KEY`, `GCP_SA_KEY` |
| Platform-specific service ID | e.g., `RAILWAY_SERVICE_ID_STAGING`, `ALIBABA_ECS_CLUSTER` |

##### Staging-to-Production Promotion Strategy

**Promotion model**: Image-based promotion. The exact same Docker image that passes staging validation is deployed to production — no rebuild. This guarantees production runs identical code to what was tested.

**Promotion flow**:

```
Push to main
    → CI passes (lint, types, tests, coverage)
    → Build Docker image: ghcr.io/{org}/{svc}:{commit-sha}
    → Push to GHCR
    → Deploy to Staging (pluggable deploy step)
    → Manual validation on staging (smoke tests, QA)

Create GitHub Release (tag: v1.x.x)
    → Re-tag existing image: ghcr.io/{org}/{svc}:v1.x.x
    → Deploy to Production (pluggable deploy step)
    → Post-deploy health check verification
```

**Environment isolation**: Each environment (staging, production) uses **separate Supabase projects** and **separate Clerk applications**. Environment variables differ per environment; the container image is identical.

| Config | Staging | Production |
|--------|---------|------------|
| `SUPABASE_URL` | Staging Supabase project | Production Supabase project |
| `SUPABASE_SERVICE_KEY` | Staging service key | Production service key |
| `CLERK_SECRET_KEY` | Staging Clerk app | Production Clerk app |
| `ENVIRONMENT` | `staging` | `production` |
| `LOG_LEVEL` | `DEBUG` | `INFO` |
| `BACKEND_CORS_ORIGINS` | Staging frontend URL | Production frontend URL |
| `SENTRY_DSN` | Staging Sentry project | Production Sentry project |

**Rollback strategy**: Deploy the previous image tag. GHCR retains all tagged images. Rollback = trigger deploy workflow with the prior `v1.x.x` tag.

**Supabase migration coordination**: Database migrations run via `supabase db push` against the target environment's Supabase project **BEFORE** deploying the new container image. The order is critical: migrate first, then deploy. This ensures the database schema is ready for the new application code.

**Pre-production checklist**:

1. All CI checks pass (lint, types, tests, 90% coverage)
2. Docker image built and pushed to GHCR
3. Image deployed and running on staging
4. Staging health checks pass (`GET /healthz` → 200, `GET /readyz` → 200)
5. Staging `GET /version` shows correct commit SHA and build time
6. Manual or automated smoke tests pass on staging
7. Supabase migrations applied to production (`supabase db push`)
8. GitHub release created with changelog
9. Production deploy triggered by release publish
10. Production health checks verified post-deploy (`GET /healthz`, `GET /readyz`)

**Reference deploy-staging.yml**:

```yaml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  ci:
    # ... CI steps (lint, type-check, test) — see ci.yml

  deploy:
    runs-on: ubuntu-latest
    needs: [ci]
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          file: backend/Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/backend:staging
          build-args: |
            GIT_COMMIT=${{ github.sha }}
            BUILD_TIME=${{ github.event.head_commit.timestamp }}

      # --- PLUGGABLE DEPLOY STEP ---
      # Uncomment ONE of the following blocks for your platform:

      # --- Railway ---
      # - name: Deploy to Railway
      #   run: railway up --service ${{ secrets.RAILWAY_SERVICE_ID_STAGING }}
      #   env:
      #     RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

      # --- Alibaba Cloud (ACR + ECS) ---
      # - name: Push to Alibaba Cloud ACR
      #   run: |
      #     docker tag ghcr.io/${{ github.repository }}/backend:${{ github.sha }} \
      #       registry.{region}.aliyuncs.com/{namespace}/{service}:${{ github.sha }}
      #     docker push registry.{region}.aliyuncs.com/{namespace}/{service}:${{ github.sha }}
      # - name: Deploy to ECS
      #   run: aliyun ecs ... # Update ECS service with new image

      # --- Google Cloud Run ---
      # - name: Deploy to Cloud Run
      #   uses: google-github-actions/deploy-cloudrun@v2
      #   with:
      #     service: ${{ secrets.GCP_SERVICE_NAME }}
      #     image: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}

      # --- Fly.io ---
      # - name: Deploy to Fly.io
      #   uses: superfly/flyctl-actions/setup-flyctl@main
      # - run: flyctl deploy --image ghcr.io/${{ github.repository }}/backend:${{ github.sha }}

      # --- Self-hosted (Docker Compose via SSH) ---
      # - name: Deploy via SSH
      #   run: |
      #     ssh ${{ secrets.DEPLOY_HOST }} "docker pull ghcr.io/${{ github.repository }}/backend:${{ github.sha }} && docker compose up -d"
```

**Reference deploy-production.yml**:

```yaml
name: Deploy to Production

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Tag release image (promote staging image)
        run: |
          docker pull ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
          docker tag ghcr.io/${{ github.repository }}/backend:${{ github.sha }} \
            ghcr.io/${{ github.repository }}/backend:${{ github.event.release.tag_name }}
          docker tag ghcr.io/${{ github.repository }}/backend:${{ github.sha }} \
            ghcr.io/${{ github.repository }}/backend:latest
          docker push ghcr.io/${{ github.repository }}/backend:${{ github.event.release.tag_name }}
          docker push ghcr.io/${{ github.repository }}/backend:latest

      # --- PLUGGABLE DEPLOY STEP ---
      # Same pattern as staging — uncomment your platform block
      # Use ${{ github.event.release.tag_name }} as the image tag
```

**Docker Compose retained for local development**: The template keeps `compose.yml` and `compose.override.yml` for local development. GHCR + GitHub Actions is for staging/production only. Developers run `docker compose up` locally, push to GitHub for deployment.

#### 4.1.20 Gateway-Ready Conventions

The template does **NOT** include a gateway. Instead, every service follows conventions that make it routable through any API gateway (Traefik, Kong, AWS ALB, Alibaba Cloud API Gateway, etc.).

**Service discoverability**:
- Every service exposes `GET /version` with `service_name`, `version`, `environment`
- Every service exposes `GET /healthz` (liveness) and `GET /readyz` (readiness)
- These endpoints require no authentication
- Gateways use these endpoints for health checking and service registration

**Routing conventions**:
- All API routes are prefixed with `/api/v1` (configurable via `API_V1_STR`)
- Service name is part of the deployment URL, not the API path
  - Correct: `https://user-service.example.com/api/v1/users`
  - Incorrect: `https://gateway.example.com/user-service/api/v1/users`
- Path-based gateway routing is possible but not the default convention

**Cross-cutting concerns** — template responsibility vs gateway responsibility:

| Concern | Template Responsibility | Gateway Responsibility |
|---------|----------------------|----------------------|
| Authentication | Clerk JWT verification per-service | Optional JWT pre-validation |
| Rate limiting | None (defer to gateway) | Per-client rate limits |
| API key management | None (Clerk handles user auth) | Machine-to-machine API keys |
| CORS | Per-service `BACKEND_CORS_ORIGINS` | Aggregate CORS if fronting multiple services |
| TLS termination | None (platform provides) | Certificate management |
| Request routing | Responds to all requests on its port | Routes by domain/path to services |
| Load balancing | None (platform provides) | Distributes across service instances |

**Service-to-service communication**:
- Services discover each other via environment variables (see Section 4.1.21)
- All inter-service calls use the shared HTTP client (Section 4.1.6), which automatically:
  - Propagates `X-Correlation-ID` and `X-Request-ID`
  - Applies timeout, retry, and circuit breaker policies
  - Logs outgoing requests with target service name and duration

**Reference: Traefik gateway configuration** (for teams wanting a self-hosted gateway):

```yaml
# compose.gateway.yml — Reference only, NOT part of the template
# Teams deploying to managed platforms typically use the platform's built-in routing.
services:
  traefik:
    image: traefik:3.6
    command:
      - --providers.docker
      - --providers.docker.exposedbydefault=false
      - --entrypoints.http.address=:80
      - --entrypoints.https.address=:443
      - --certificatesresolvers.le.acme.tlschallenge=true
      - --certificatesresolvers.le.acme.email=${ACME_EMAIL}
      - --certificatesresolvers.le.acme.storage=/certificates/acme.json
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certificates:/certificates

# Rate limiting middleware (apply via labels on services):
# traefik.http.middlewares.rate-limit.ratelimit.average=100
# traefik.http.middlewares.rate-limit.ratelimit.burst=50
# traefik.http.middlewares.rate-limit.ratelimit.period=1m
```

#### 4.1.21 Service URL Configuration

When a service needs to call another service, the target URL is configured via environment variable following the pattern: `{SERVICE_NAME}_URL`.

**Config additions** to `app/core/config.py`:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `{SERVICE_NAME}_URL` | `AnyHttpUrl` | None | Base URL for the target service. One env var per dependency. |

**Example `.env`**:
```env
USER_SERVICE_URL=https://user-service.railway.internal
BILLING_SERVICE_URL=https://billing-service.railway.internal
```

**Usage in code**:
```python
from app.core.config import settings

async def get_user(http: HttpClientDep, user_id: str):
    url = settings.USER_SERVICE_URL
    if not url:
        raise ServiceError(
            status_code=503,
            error="SERVICE_UNAVAILABLE",
            message="User service not configured",
            code="SERVICE_NOT_CONFIGURED",
        )
    response = await http.get(f"{url}/api/v1/users/{user_id}")
    return response.json()
```

This is intentionally simple — no service registry, no DNS-based discovery, no service mesh. Just environment variables pointing to URLs. This works because container platforms provide stable internal URLs for services within the same project/cluster.

### 4.2 WITH_UI Flag

**Two mechanisms**:

1. **Copier template variable** (`with_ui: bool`): Controls whether frontend files are generated at all when creating a new project from the template. Uses Jinja conditional file inclusion:
   ```
   {% if with_ui %}frontend{% endif %}/
   ```

2. **Runtime env var** (`WITH_UI=true/false`): Controls Docker Compose profile and CI behaviour when the files already exist. Allows a full-stack project to be run in backend-only mode for certain environments.

**Backend isolation rule**: The backend Python code MUST NOT import from, reference, or depend on any frontend artifact. No OpenAPI client generation trigger, no frontend build step in backend Dockerfile, no frontend URL in backend config (except CORS origins which are optional).

### 4.3 Sample Entity Resource

The Entity is a minimal CRUD resource demonstrating all conventions:

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | UUID | Primary key, auto-generated |
| `title` | string | Required, max 255 chars |
| `description` | string | Optional, max 1000 chars |
| `owner_id` | string | Clerk user ID, set from Principal |
| `created_at` | timestamptz | Auto-set on insert |
| `updated_at` | timestamptz | Auto-set on insert and update |

**Endpoints**:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/entities` | Required | Create entity (owner_id from JWT) |
| `GET` | `/api/v1/entities` | Required | List entities (own only, paginated) |
| `GET` | `/api/v1/entities/{id}` | Required | Get entity by ID (ownership check) |
| `PATCH` | `/api/v1/entities/{id}` | Required | Update entity (ownership check) |
| `DELETE` | `/api/v1/entities/{id}` | Required | Delete entity (ownership check) |

**Ownership**: Users can only CRUD their own entities. Enforced by Supabase RLS policies using the `owner_id` column.

---

## 5. Technical Specification

### Architecture Pattern

**Layered service architecture** with strict separation:

```
Routes (API layer) → Services (Business logic) → Supabase Client (Data layer)
         ↑
    Dependencies (Core: auth, config, logging, errors)
```

- **Routes**: HTTP handling, request validation, response serialization. No business logic.
- **Services**: Business rules, data orchestration. No HTTP concerns.
- **Supabase Client**: Data access via supabase-py. No business logic.
- **Core**: Cross-cutting concerns injected via FastAPI dependencies.

**Rationale**: Matches the existing template's separation of `api/routes/` → `crud.py`, upgraded to a proper service layer. Keeps routes thin and business logic testable in isolation.

### Architecture Decision: Migrations — Supabase CLI over Alembic

**Decision**: Use **Supabase CLI native migrations** (`supabase/migrations/*.sql`) instead of Alembic.

**Rationale**:

| Factor | Alembic | Supabase CLI | Winner |
|--------|---------|-------------|--------|
| ORM coupling | Requires SQLAlchemy models for autogenerate | Raw SQL — no ORM needed | **Supabase CLI** (we removed SQLAlchemy) |
| Supabase features | Cannot generate RLS policies, functions, triggers | Full support for all Supabase/PostgreSQL features | **Supabase CLI** |
| Local development | Requires running PostgreSQL directly | `supabase start` gives full local Supabase (auth, storage, etc.) | **Supabase CLI** |
| CI/CD | `alembic upgrade head` against remote DB | `supabase db push` against remote project | Tie |
| Ecosystem fit | Foreign tool in Supabase ecosystem | Native tool, matches Supabase dashboard | **Supabase CLI** |
| Python dependency | `alembic` + `sqlalchemy` packages | No Python dependency (CLI is a Go binary) | **Supabase CLI** |

Since we're replacing SQLAlchemy/SQLModel with `supabase-py` (a REST client, not an ORM), Alembic's autogenerate feature — its primary value — no longer works. There are no Python model classes to diff against. Supabase CLI migrations are raw SQL files, version-controlled in `supabase/migrations/`, and natively integrated with `supabase db push` for deployment.

**Migration workflow**:
```bash
supabase migration new create_entities   # Creates timestamped .sql file
# Edit the SQL file
supabase db reset                         # Apply locally (drops + recreates)
supabase db push                          # Apply to remote project
```

### Architecture Decision: Platform-Agnostic Deployment over Platform-Specific

**Decision**: Use **platform-agnostic container deployment** (GHCR + pluggable GitHub Actions deploy step) instead of locking to a specific cloud provider.

**Rationale**:

| Factor | Platform-specific (e.g., Railway, Cloud Run) | Platform-agnostic (GHCR + pluggable deploy) | Winner |
|--------|----------------------------------------------|---------------------------------------------|--------|
| Portability | Locked to one vendor's CLI/API | Works with any container platform | **Platform-agnostic** |
| Team flexibility | All teams must use same platform | Teams choose per-project (Alibaba Cloud, Railway, etc.) | **Platform-agnostic** |
| Template maintenance | Must maintain platform-specific workflows | One CI workflow + commented deploy examples | **Platform-agnostic** |
| Developer experience | Optimised for one platform | Slightly more initial setup | Platform-specific |
| Vendor lock-in | High (platform CLI, config files) | Low (standard Docker + GHCR) | **Platform-agnostic** |

Since the template uses managed services (Supabase for database, Clerk for auth), the backend is a stateless container. Any platform that runs Docker containers works. The template provides a production-ready Dockerfile, GHCR integration, and reference deploy steps for multiple platforms. Teams uncomment the deploy step for their chosen platform.

**Escape hatch**: The template retains Docker Compose for local development. The Dockerfile is standard and works with any container runtime.

### Architecture Decision: Gateway-Ready over Gateway-Inclusive

**Decision**: Make services **gateway-ready** (follow conventions) rather than including a gateway implementation in the template.

**Rationale**:

| Factor | Gateway-inclusive | Gateway-ready | Winner |
|--------|------------------|---------------|--------|
| Template simplicity | Adds gateway service, routing config, extra container | No additional components | **Gateway-ready** |
| Deployment flexibility | Couples template to specific gateway (Traefik/Kong) | Works with any gateway or direct access | **Gateway-ready** |
| Platform compatibility | May conflict with platform's built-in routing | Complements any platform's routing | **Gateway-ready** |
| Single-service use case | Unnecessary overhead | Service works standalone | **Gateway-ready** |
| Multi-service use case | Gateway is an operational concern, not per-service | Services bring conventions, team adds gateway | **Gateway-ready** |

A gateway is a deployment-level concern that varies by team and scale. Including one in the template would either (a) couple all services to one deployment model, or (b) require maintaining multiple gateway configurations. Instead, the template ensures every service follows conventions (versioned APIs, health endpoints, correlation IDs, CORS configuration) that make it routable through any gateway a team chooses to adopt.

### API Endpoints

#### `GET /healthz`
**Purpose**: Liveness probe.

**Response** (200 OK):
```json
{"status": "ok"}
```

#### `GET /readyz`
**Purpose**: Readiness probe with dependency checks.

**Response** (200 OK):
```json
{
  "status": "ready",
  "checks": {
    "supabase": "ok"
  }
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "not_ready",
  "checks": {
    "supabase": "error"
  }
}
```

#### `GET /version`
**Purpose**: Build metadata.

**Response** (200 OK):
```json
{
  "version": "0.1.0",
  "commit": "abc1234",
  "build_time": "2026-02-27T10:00:00Z",
  "environment": "production"
}
```

#### `POST /api/v1/entities`
**Purpose**: Create a new entity.
**Auth**: Required (Clerk JWT).

**Request**:
```json
{
  "title": "My Entity",
  "description": "Optional description"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Entity",
  "description": "Optional description",
  "owner_id": "user_2abc123",
  "created_at": "2026-02-27T10:00:00Z",
  "updated_at": "2026-02-27T10:00:00Z"
}
```

**Errors**: 401 (no auth), 422 (validation)

#### `GET /api/v1/entities`
**Purpose**: List authenticated user's entities.
**Auth**: Required.
**Query params**: `offset` (int, default 0), `limit` (int, default 20, max 100)

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "...",
      "title": "...",
      "description": "...",
      "owner_id": "user_2abc123",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "count": 42
}
```

#### `GET /api/v1/entities/{id}`
**Purpose**: Get single entity by ID.
**Auth**: Required. Ownership check.

**Response** (200 OK): Single `EntityPublic` object.
**Errors**: 401 (no auth), 404 (not found or not owned)

#### `PATCH /api/v1/entities/{id}`
**Purpose**: Update entity fields.
**Auth**: Required. Ownership check.

**Request**:
```json
{
  "title": "Updated Title"
}
```

**Response** (200 OK): Updated `EntityPublic` object.
**Errors**: 401, 404, 422

#### `DELETE /api/v1/entities/{id}`
**Purpose**: Delete entity.
**Auth**: Required. Ownership check.

**Response**: 204 No Content.
**Errors**: 401, 404

### Data Models

**Pydantic models** (see Section 4.1.18 for the full pattern).

### Database Schema

```sql
-- supabase/migrations/20260227000000_create_entities.sql

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    owner_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for owner-scoped queries
CREATE INDEX idx_entities_owner_id ON entities(owner_id);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER entities_updated_at
    BEFORE UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Row-Level Security
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see their own entities
-- (service role key bypasses RLS for admin operations)
CREATE POLICY "Users can view own entities"
    ON entities FOR SELECT
    USING (owner_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can insert own entities"
    ON entities FOR INSERT
    WITH CHECK (owner_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can update own entities"
    ON entities FOR UPDATE
    USING (owner_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can delete own entities"
    ON entities FOR DELETE
    USING (owner_id = current_setting('request.jwt.claim.sub', true));
```

> **Note**: When using the service role key (as this backend does), RLS is bypassed. The RLS policies are defined for direct PostgREST access patterns and as documentation of the intended access model. Ownership checks in the service layer provide the primary enforcement when using the service key.

---

## 6. Integration Points

### Dependencies

- **Internal**: None (standalone template)
- **External**:
  - **Supabase**: Database (PostgreSQL), REST API via supabase-py
  - **Clerk**: JWT verification, user identity provider
  - **GitHub Container Registry (GHCR)**: Docker image storage and versioning
  - **Container host (team choice)**: Alibaba Cloud ECS/ACR, Railway, Google Cloud Run, Fly.io, or self-hosted — any platform that runs Docker containers
  - **Sentry** (optional): Error tracking and performance monitoring
- **New Python libraries** (replacing existing):
  - `supabase` >=2.0 — Supabase Python client
  - `clerk-backend-api` >=1.0 — Clerk SDK for JWT verification
  - `structlog` >=24.0 — Structured logging
  - `httpx` >=0.27 — Async HTTP client (already a transitive dep, now explicit)
- **Removed Python libraries**:
  - `sqlmodel`, `sqlalchemy`, `alembic`, `psycopg` — replaced by Supabase
  - `pwdlib`, `argon2-cffi`, `bcrypt` — no local password handling
  - `pyjwt` — replaced by Clerk SDK
  - `emails`, `jinja2` — no email sending in template
- **New CLI tools**:
  - `supabase` CLI — local development and migrations

### Events/Webhooks

None in MVP. Template provides the patterns; services add their own events.

---

## 7. UX Specifications

Not applicable for the backend-only template. When WITH_UI=true, the existing React frontend shell is preserved with these modifications:

- Strip all user management pages (login, signup, password recovery, user settings)
- Strip all Item-related components
- Keep: layout shell, routing skeleton, theme provider, toast notifications
- Add: Entity list/detail pages as sample CRUD UI
- Auth: Replace local JWT auth with Clerk's `@clerk/clerk-react` provider
- The frontend UX design is deferred to a separate PRD if needed

---

## 8. Implementation Guidance

### Follow Existing Patterns

**Based on codebase analysis** (reference files found):
- **Config pattern**: Extend from `backend/app/core/config.py` — keep `BaseSettings` approach, replace PostgreSQL vars with Supabase vars
- **Route pattern**: Follow `backend/app/api/routes/items.py` — thin handlers delegating to service layer
- **Dependency pattern**: Follow `backend/app/api/deps.py` — `Annotated[T, Depends()]` typed dependencies
- **Model pattern**: Follow `backend/app/models.py` — `Base → Create → Update → Public` layered models
- **Test pattern**: Follow `backend/tests/conftest.py` — fixture-based setup with dependency overrides

### Recommended Implementation Order

**Phase 1 — Core Infrastructure** (backend/app/core/):
1. `config.py` — New Settings with Supabase + Clerk env vars
2. `errors.py` — Standard error models + global exception handlers
3. `logging.py` — structlog configuration
4. `middleware.py` — Request ID, security headers, request logging
5. `supabase.py` — Client initialization + FastAPI dependency
6. `auth.py` — Clerk JWT verification + Principal dependency
7. `http_client.py` — Shared httpx wrapper

**Phase 2 — API Layer**:
8. `api/deps.py` — Typed dependency declarations
9. `api/routes/health.py` — `/healthz`, `/readyz`, `/version`
10. `models/entity.py` — Entity Pydantic models
11. `services/entity_service.py` — Entity CRUD via Supabase
12. `api/routes/entities.py` — Entity REST endpoints

**Phase 3 — Main App**:
13. `main.py` — FastAPI app with lifespan, routers, middleware

**Phase 4 — Database**:
14. `supabase/migrations/` — Entity table migration
15. `supabase/config.toml` — Local Supabase config

**Phase 5 — Tests**:
16. Unit tests for all core modules (config, auth, errors, services)
17. Integration tests for health and entity endpoints
18. Test fixtures: mock Supabase client, mock Clerk auth

**Phase 6 — Docker & CI**:
19. Update backend Dockerfile (remove Alembic, add build args)
20. Update compose.yml (remove PostgreSQL, add profiles)
21. Update CI workflows (gate frontend steps)

**Phase 7 — Cleanup**:
22. Remove: all user/auth/login/password/email code and routes
23. Remove: Item model, CRUD, routes
24. Remove: SQLAlchemy, Alembic, psycopg dependencies
25. Remove: pwdlib, pyjwt, emails dependencies
26. Update: CLAUDE.md, README.md

**Phase 8 — Copier Template** (optional, can be separate story):
27. Add copier.yml with template variables
28. Add Jinja conditionals for WITH_UI file inclusion

**Phase 9 — Deployment**:
29. Update backend Dockerfile (multi-stage build, OCI labels, non-root user, build args)
30. Create `deploy-staging.yml` GitHub Action (GHCR build/push + pluggable deploy step)
31. Create `deploy-production.yml` GitHub Action (re-tag image + pluggable deploy step)
32. Create `.env.example` with all required env vars documented
33. Update README.md with deployment setup instructions (GHCR, environment promotion, platform examples)

**Phase 10 — Gateway Documentation**:
34. Document gateway-ready conventions in README
35. Add reference `compose.gateway.yml` for self-hosted Traefik gateway (documentation only, not shipped)
36. Document service-to-service communication pattern with env var URLs

### Code Pattern Examples

**Clerk auth dependency** (based on Clerk SDK docs):

```python
# app/core/auth.py
from clerk_backend_api import Clerk
from clerk_backend_api.security import authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions
from fastapi import Request, HTTPException
from app.core.config import settings
from app.models.auth import Principal

_clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY.get_secret_value())

async def get_current_principal(request: Request) -> Principal:
    """Verify Clerk JWT and extract principal."""
    request_state = _clerk.authenticate_request(
        request,
        AuthenticateRequestOptions(
            authorized_parties=settings.CLERK_AUTHORIZED_PARTIES
        )
    )
    if not request_state.is_signed_in:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    payload = request_state.payload
    return Principal(
        user_id=payload.get("sub"),
        org_id=payload.get("org_id"),
        roles=payload.get("roles", []),
        session_id=payload.get("sid"),
    )
```

**Standard error handler** (new pattern):

```python
# app/core/errors.py
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

class ServiceError(Exception):
    def __init__(self, status_code: int, error: str, message: str, code: str):
        self.status_code = status_code
        self.error = error
        self.message = message
        self.code = code

async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
            "code": exc.code,
            "request_id": request.state.request_id,
        },
    )
```

### Security Considerations

- **Clerk secret key**: Stored as `SecretStr`, never logged, never serialized
- **Supabase service key**: Bypasses RLS — only used server-side, never exposed to clients
- **JWT validation**: Always verify signature, expiry, and authorized parties
- **SQL injection**: Not applicable — supabase-py uses parameterized queries via PostgREST
- **CORS**: Strict origin list from env vars. No wildcards in production.
- **Secrets in logs**: structlog configured to redact `SecretStr` fields
- **Dependency supply chain**: Pin exact versions in `pyproject.toml` lock file

### Observability

- **Logs**: structlog JSON to stdout → collected by container platform
- **Metrics**: `/readyz` latency and success rate (external monitoring)
- **Alerts**: Sentry for unhandled exceptions; readiness failures for Supabase connectivity
- **Tracing**: Request ID and correlation ID in all logs for cross-service tracing

---

## 9. Testing Strategy

### Unit Tests
- [ ] `test_config.py` — Settings validation, env var parsing, production guards
- [ ] `test_auth.py` — Clerk JWT verification: valid token, expired, missing, malformed
- [ ] `test_errors.py` — Error model serialization, exception handler formatting
- [ ] `test_entity_service.py` — Entity CRUD logic with mocked Supabase client
- [ ] `test_middleware.py` — Request ID generation, security headers, correlation ID
- [ ] `test_http_client.py` — Timeout, retry, header propagation

### Integration Tests
- [ ] `test_health.py` — `/healthz` returns 200; `/readyz` returns 200 with healthy Supabase, 503 when unhealthy; `/version` returns build metadata
- [ ] `test_entities.py` — Full CRUD lifecycle; auth required; ownership enforcement; pagination; validation errors return standard shape
- [ ] `test_error_responses.py` — All error status codes return standard JSON shape

### E2E Tests (only when WITH_UI=true)
- [ ] Frontend can authenticate via Clerk and make API calls
- [ ] Entity CRUD works through the UI

### Test Fixtures

**Mock Supabase**: Override `SupabaseDep` with a mock that returns controlled responses. No real Supabase connection in unit tests.

**Mock Clerk**: Override `PrincipalDep` with a fixture that returns a predetermined `Principal`. Integration tests use a test principal injected via dependency override.

**Test configuration**: Separate `.env.test` with test-specific values. `ENVIRONMENT=local` in tests.

### Manual Verification

Map to acceptance criteria:
- [ ] **AC: Backend-only startup**: `WITH_UI=false docker compose up` → only backend runs
- [ ] **AC: Full-stack startup**: `WITH_UI=true docker compose --profile ui up` → both run
- [ ] **AC: Valid Clerk JWT**: curl with valid token → 200
- [ ] **AC: Invalid JWT**: curl without token → 401 with standard error shape
- [ ] **AC: Entity CRUD**: POST → GET → PATCH → DELETE lifecycle
- [ ] **AC: Operational endpoints**: curl `/healthz`, `/readyz`, `/version` without auth → 200
- [ ] **AC: CI**: Push to branch, verify backend-only CI passes; toggle WITH_UI=true, verify full CI passes
- [ ] **AC: Deploy staging**: Push to main, verify Docker image built and pushed to GHCR, verify deploy step triggers
- [ ] **AC: Promote to production**: Create GitHub release, verify staging image re-tagged with version, verify production deploy triggers
- [ ] **AC: Rollback**: Deploy previous image tag, verify production restored to prior version
- [ ] **AC: Service metadata**: GET /version returns service_name, version, commit, build_time, environment
- [ ] **AC: Correlation propagation**: Service-to-service call propagates X-Correlation-ID header

---

## 10. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Clerk SDK `authenticate_request` requires httpx.Request, not Starlette Request | High | Medium | Wrap Starlette request in httpx.Request adapter; or use raw JWT verification with JWKS. Spike this first. |
| Supabase-py async client maturity — bugs or missing features | Medium | Low | Use sync client initially; supabase-py 2.x is stable. Fall back to raw httpx + PostgREST if needed. |
| Copier conditional file inclusion complexity | Low | Medium | Keep Jinja conditions simple (single boolean). Test template generation in CI. |
| Docker Compose profiles not supported in older Docker versions | Medium | Low | Require Docker Compose v2.x (released 2022). Document in README. |
| RLS policies defined but bypassed by service key — false sense of security | Medium | Medium | Document clearly that service-layer ownership checks are the primary enforcement. RLS is defense-in-depth for direct DB access. |
| Breaking change if existing services depend on current template structure | High | Low | This is a new template, not a migration of existing services. Document migration path separately. |
| `structlog` learning curve for team | Low | Low | Provide clear examples in template code. structlog API is stdlib-compatible. |
| GHCR rate limiting on image pulls in CI | Low | Low | Use GitHub Actions Docker layer cache. Container platforms cache pulled images. |
| Platform-specific deploy step maintenance across multiple platforms | Medium | Medium | Keep deploy steps minimal (2-3 lines each). Document alternatives as commented YAML blocks. Teams only uncomment one. |
| Service-to-service latency when using public URLs instead of internal networking | Medium | Low | Document platform-specific internal networking (e.g., Railway `.railway.internal`, Alibaba Cloud VPC endpoints). Fall back to public URLs if internal networking is unavailable. |
| Team unfamiliarity with container deployment and GHCR | Low | Medium | Provide step-by-step README per platform. GHCR uses standard Docker push/pull. Deployment is one workflow file to uncomment. |
| Gateway-ready conventions insufficient for complex routing requirements | Medium | Low | Document upgrade path: when direct service URLs are outgrown, add a Traefik or cloud-native API gateway. Conventions are gateway-agnostic by design. |

---

## 11. References

### Context7 Documentation

- **Clerk SDK Python** (`/clerk/clerk-sdk-python`): `authenticate_request()` pattern — verify JWT via JWKS, extract `sub`, `sid`, `org_id` claims. Uses `AuthenticateRequestOptions` for `authorized_parties`.
- **Supabase Python** (`/supabase/supabase-py`): Table CRUD via `.table("name").insert/select/update/delete().execute()`. Supports `.eq()`, `.range()`, `.single()` query builders. Returns `.data` and `.count`.
- **Copier** (`/copier-org/copier`): Conditional file inclusion via Jinja in filenames (`{% if var %}filename{% endif %}.jinja`). `_exclude` patterns in copier.yml. Questions with types, defaults, help text.

### Research Sources

- [fastapi-clerk-middleware](https://github.com/OSSMafia/fastapi-clerk-middleware): Community middleware for Clerk + FastAPI. Validates JWT against JWKS. Useful reference but we'll use the official SDK for maintainability.
- [Clerk Python SDK README](https://github.com/clerk/clerk-sdk-python/blob/main/README.md): Official `authenticate_request` usage. Key insight: requires `httpx.Request` object, may need adapter for Starlette.
- [FastAPI + Supabase patterns](https://dev.to/j0/setting-up-fastapi-with-supabasedb-2jm0): Supabase as PostgreSQL backend with FastAPI. Confirms supabase-py + Alembic is common but Supabase CLI is preferred when not using SQLAlchemy ORM.
- [fastapi-clerk-auth on PyPI](https://pypi.org/project/fastapi-clerk-auth/): Lightweight alternative for JWKS-based JWT verification without the full Clerk SDK dependency.

### Codebase References

- Config pattern: `backend/app/core/config.py` — Pydantic BaseSettings with env validation, computed fields, environment-specific guards
- Route pattern: `backend/app/api/routes/items.py` — Thin handlers with SessionDep/CurrentUser dependencies, HTTPException for errors
- Dependency injection: `backend/app/api/deps.py` — `Annotated[T, Depends()]` pattern, OAuth2PasswordBearer, `get_current_user()` chain
- Model pattern: `backend/app/models.py` — `Base → Create → Update → Public` layered Pydantic/SQLModel classes, UUID primary keys, timezone-aware timestamps
- CRUD pattern: `backend/app/crud.py` — Pure functions with keyword-only args, session-based operations
- Test fixtures: `backend/tests/conftest.py` — Session-scoped DB, module-scoped client, pre-authenticated header fixtures
- Docker: `compose.yml` — Multi-service with health checks, Traefik routing, env vars from `.env`
- CI: `.github/workflows/test-backend.yml` — Python setup, docker compose, migration, pytest with coverage
- Deploy: `.github/workflows/deploy-staging.yml` — Self-hosted runner staging deployment (to be replaced)
- Deploy: `.github/workflows/deploy-production.yml` — Self-hosted runner production deployment (to be replaced)

### Deployment References

- [GitHub Container Registry (GHCR) documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) — Docker image storage with GitHub Actions integration
- [Docker multi-stage build best practices](https://docs.docker.com/build/building/best-practices/) — Optimising Dockerfile for production containers
- [OCI image specification](https://github.com/opencontainers/image-spec/blob/main/annotations.md) — Standard labels for container images
- [Traefik API Gateway](https://doc.traefik.io/traefik/) — Reference gateway for self-hosted deployments
- [Alibaba Cloud Container Registry (ACR)](https://www.alibabacloud.com/product/container-registry) — Container registry for Alibaba Cloud deployments
- [Alibaba Cloud Elastic Container Service (ECS)](https://www.alibabacloud.com/product/ecs) — Container hosting on Alibaba Cloud

---

## Quality Checklist

- [x] Self-contained with full context
- [x] INVEST user stories (8 stories)
- [x] Complete Gherkin ACs (happy + edge + errors + deployment — 14 scenarios)
- [x] API contracts with schemas (all 8 endpoints defined)
- [x] Error handling defined (unified shape, status mapping, validation details)
- [x] Data models documented (Entity schema + Pydantic models)
- [x] Security addressed (Clerk JWT, Supabase service key, CORS, headers, secrets)
- [x] Performance specified (<50ms health, <200ms CRUD, <5s cold start)
- [x] Testing strategy outlined (unit + integration + E2E, fixtures, coverage)
- [x] Out-of-scope listed (updated: gateway-inclusive, platform-specific, K8s, shared packages)
- [x] References populated (Context7, web research, codebase, deployment)
- [x] Matches project conventions (naming, structure, patterns from existing template)
- [x] Quantifiable requirements (no vague terms)
- [x] Architecture decisions documented (Supabase CLI migrations, platform-agnostic deployment, gateway-ready)
- [x] Full canonical conventions list (21 convention categories)
- [x] Deployment strategy specified (platform-agnostic containerised deployment)
- [x] CI/CD pipeline covers build, push, deploy (GHCR + pluggable deploy step)
- [x] Environment promotion documented (staging → production with image-based promotion)
- [x] Rollback strategy documented (deploy previous image tag)
- [x] Gateway-ready conventions defined (service discoverability, routing, cross-cutting concerns)
- [x] Service-to-service communication pattern documented (env var URLs + HTTP client)
