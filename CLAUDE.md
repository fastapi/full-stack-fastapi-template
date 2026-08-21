# Engineering rules

## Stack

- **Backend**: FastAPI + SQLModel (Pydantic + SQLAlchemy) + Alembic + Postgres. Package/venv managed with `uv` from `backend/`.
- **Frontend**: React + TanStack Router/Query + generated OpenAPI client (`@hey-api/openapi-ts`) + shadcn/radix + Tailwind. Managed with `bun` from `frontend/` (or repo root via `bun run --filter frontend <script>`).
- **Local services**: `docker compose up` runs Postgres + Mailpit (see `compose.yml`). App servers run outside Docker in dev.

## Known gotchas

- `app.main` (`backend/app/main.py`) unconditionally mounts a static frontend build at `backend/app/frontend`. That directory only exists after a frontend build is copied in (normally a Docker build step). Running `uv run fastapi dev app/main.py` in a fresh dev checkout without that directory logs a `UserWarning` but still starts — if it ever hard-fails instead, generate the OpenAPI schema from `app.api.main.api_router` directly (see `scripts/generate-client.sh` for the shape) rather than importing `app.main`.
- `scripts/generate-client.sh` requires the backend importable and a running Postgres (`docker compose up`). Regenerate the client (`bun run --filter frontend generate-client`) any time backend Pydantic/SQLModel schemas change — the frontend has no fallback typing.
- **`uv run bash scripts/test.sh` wipes all `User` and `Item` rows** in whatever database `DATABASE_URL` points to. `tests/conftest.py`'s session-scoped `db` fixture unconditionally deletes both tables at teardown. Locally this is the *same* Postgres instance/database used for interactive dev testing — there's no separate test DB in this local setup. Never run the backend test suite against a database with data you want to keep; if you just did, re-seed with `uv run bash scripts/prestart.sh` (restores roles/permissions/first-admin, but any other manually-created accounts are gone for good).

## Authorization (RBAC)

This project uses role-based access control. The design lives in `openspec/changes/add-rbac/design.md`; the human-facing writeup (permission matrix, setup, seeding) lives in `docs/AUTHORIZATION.md`. The rules below are what keep it maintainable — read them before touching any permission check.

**Single source of truth for permission codes and role grants**: `backend/app/core/rbac.py`. Every permission code and every role→permission grant is defined there once, as constants — nowhere else. The frontend mirrors the same codes as a `PERMISSIONS` constant object in `frontend/src/utils.ts`. Never hardcode a permission string (`"users:list"`, `"metrics:view"`, etc.) anywhere else in either codebase — import the constant.

**Backend checks always go through `require_permission(code)`** (`backend/app/api/deps.py`), used as a route dependency. The one exception is item-ownership fallback (`owner_id == current_user.id`) in `app/api/routes/items.py`, which stays inline because it's data-scoped, not role-scoped — everything else goes through the dependency. Never write an inline `if current_user.role.slug == "admin"` check in a route; that's exactly the pattern this replaced.

**Frontend checks always go through `hasPermission(user, code)`** (`frontend/src/utils.ts`). Never branch on `user.role === "..."` in a component — role names are for display (badges, select options), not authorization decisions.

**Unauthorized direct navigation shows the shared `AccessDenied` page** (routed at `/forbidden`), not a silent redirect to `/` and not a raw error. Every route `beforeLoad` guard redirects there on a failed permission check.

**To add a new role**: add one row to the seed data (migration + `init_db`) and one entry to `ROLE_PERMISSIONS` in `rbac.py`. No route or component should need to change.

**To add a new permission**: add one constant in `rbac.py` (and the mirrored `PERMISSIONS` entry in `utils.ts`), add it to whichever roles should have it in `ROLE_PERMISSIONS`/seed data, and use it at exactly the route(s) or component(s) it protects via `require_permission`/`hasPermission`. That's the whole change — if you find yourself editing more than the seed data, `rbac.py`, `utils.ts`, and the specific protected site(s), stop and reconsider.

**Comments**: authorization code stays comment-free by default — the constants and dependency names should make the model obvious on their own. Add a comment only where the *why* genuinely isn't visible in the code (e.g., why several unrelated checks share the `system:admin` catch-all). Don't add a comment that restates what a function or constant name already says.

## General

- No comments unless the *why* is non-obvious (see above) — this applies repo-wide, not just to authorization code.
- Don't add abstractions, config flags, or generalized helpers for a single call site. Three similar lines beat a premature abstraction.
- Keep changes scoped to what's asked; don't drive-by refactor unrelated code in the same diff.
