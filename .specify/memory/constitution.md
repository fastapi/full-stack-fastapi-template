<!--
## Sync Impact Report

**Version change**: N/A (initial ratification) -> 1.0.0

**Modified principles**: N/A — initial fill-in from blank template.

**Added sections**:
- Core Principles (5 principles defined)
- Technology Stack
- Development Workflow
- Governance

**Removed sections**: None (template placeholders replaced throughout)

**Templates requiring updates**:
- .specify/templates/plan-template.md  ✅ no changes needed — Constitution Check
  gate is a per-feature placeholder, not project-specific
- .specify/templates/spec-template.md  ✅ no changes needed
- .specify/templates/tasks-template.md ✅ no changes needed
- .specify/templates/agent-file-template.md ✅ no changes needed
- .specify/templates/checklist-template.md  ✅ no changes needed

**Deferred TODOs**: None
-->

# Full Stack FastAPI Template Constitution

## Core Principles

### I. Full-Stack Cohesion

The frontend and backend are a single product. The OpenAPI spec and Pydantic schemas
are the authoritative interface between them.

- The auto-generated frontend client MUST be regenerated whenever backend endpoints
  or schemas change.
- Frontend and backend MUST be deployed together; no partial deploys that leave the
  client out of sync with the API.
- Breaking API changes require updating both sides before a PR is merged.

**Rationale**: Drift between the generated client and the actual API is a silent
failure — it produces runtime errors, not build errors, and surfaces only in production.

### II. Contract-First API Design

All API endpoints MUST have complete Pydantic request/response schemas defined before
implementation begins.

- Schema changes MUST be reviewed for downstream frontend impact before merging.
- Every endpoint MUST appear in FastAPI's auto-generated OpenAPI spec — no undocumented
  routes.
- Response models MUST explicitly exclude sensitive fields (e.g., hashed passwords)
  via Pydantic model configuration, not ad-hoc filtering.

**Rationale**: Explicit contracts prevent accidental data leakage and allow the
frontend client generator to produce correct, type-safe code.

### III. Security by Default

Security MUST be present in the default state of the codebase, not retrofitted.

- All non-public endpoints MUST be protected by JWT authentication.
- Secrets (`SECRET_KEY`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`) MUST be
  managed through environment variables only — never hardcoded, never committed.
- Password storage MUST use the project's built-in bcrypt hashing. Plaintext,
  MD5, or SHA-1 passwords are prohibited.
- The placeholder values (`changethis`) MUST be replaced before any deployment,
  including staging.

**Rationale**: This project is a template — insecure defaults are copied directly
into downstream production systems.

### IV. Test-Enforced Quality

All changes MUST pass automated tests before merging. Tests are infrastructure,
not optional extras.

- Backend: pytest covers all API endpoints via integration tests against a real
  test database (not mocks).
- Frontend: Playwright covers all critical user journeys end-to-end.
- CI MUST run the full test suite on every PR; green CI is a non-negotiable merge
  prerequisite.
- New API endpoints MUST include pytest tests. New user journeys MUST include
  Playwright coverage.

**Rationale**: A full-stack template ships with a working test harness as a
reference. Contributors who add features without tests break that contract.

### V. Docker-First Infrastructure

Docker Compose is the single source of truth for the full service topology
(backend, frontend, database, proxy, mail).

- All services MUST be runnable with `docker compose up` in both development and
  production configurations.
- Environment configuration MUST flow exclusively through `.env` files —
  no environment-specific branching in application code.
- TLS termination MUST be handled by Traefik; application code MUST NOT implement
  its own TLS.
- Production deploys MUST use the production Docker Compose configuration with
  secrets injected via environment variables, not `.env` files checked into the repo.

**Rationale**: Reproducible environments eliminate "works on my machine" failures
and make the template immediately usable without local toolchain prerequisites.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend language | Python 3.11+ |
| Backend framework | FastAPI |
| ORM | SQLModel |
| Validation | Pydantic v2 |
| Database | PostgreSQL |
| Migrations | Alembic |
| Backend tests | pytest |
| Frontend framework | React 18+ |
| Frontend language | TypeScript |
| Bundler | Vite |
| Styling | Tailwind CSS + shadcn/ui |
| E2E tests | Playwright |
| Container orchestration | Docker Compose |
| Reverse proxy / TLS | Traefik |
| CI/CD | GitHub Actions |
| Local email testing | Mailcatcher |

All dependency versions MUST be pinned (`==` for Python, exact versions for npm).
Upgrades require running the full test suite before merging.

## Development Workflow

- **New features**: Feature branch -> PR -> CI green -> review -> merge to master.
  Never push directly to master.
- **API changes**: Update Pydantic schemas -> implement endpoint -> regenerate
  frontend client (`./scripts/generate-client.sh` or equivalent) -> update
  Playwright tests if user-facing.
- **Database changes**: Write Alembic migration -> verify migration applies and
  rolls back cleanly -> never edit already-merged migrations.
- **Environment setup**: Copy `.env` example files -> replace all `changethis`
  values -> `docker compose up`.
- **Pre-merge gate**: CI passes, frontend client regenerated (if API changed),
  no secrets in diff, migrations tested forward and backward.

## Governance

This constitution supersedes all other practices and informal conventions.
It applies to all contributors and all feature work.

**Amendment procedure**: Propose changes via PR with an updated constitution and
an embedded Sync Impact Report (HTML comment at top of file). Requires explicit
approval before merging. Every amendment MUST increment the version per the policy
below.

**Versioning policy**:
- MAJOR: Principle removal, redefinition, or backward-incompatible governance change.
- MINOR: New principle or section added, or material guidance expansion.
- PATCH: Clarifications, wording corrections, non-semantic refinements.

**Compliance**: All PRs MUST verify compliance with the Core Principles above.
The Constitution Check section in `plan.md` MUST reference and pass the active
principles before Phase 0 research begins. Violations MUST be justified in the
Complexity Tracking table of the plan.

For runtime development guidance see `development.md` and the per-component READMEs:
`backend/README.md`, `frontend/README.md`, `deployment.md`.

**Version**: 1.0.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07
