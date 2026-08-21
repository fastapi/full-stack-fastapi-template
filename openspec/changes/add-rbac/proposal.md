## Why

The template gates privileged actions with a boolean `is_superuser`. That is enough for a demo admin, but it cannot express distinct privileges, cannot hide only some UI, and forces every new sensitive feature into another superuser check. We need role-based access control so authorized users can reach sensitive API endpoints and UI sections, and everyone else cannot.

## What Changes

- Replace the `is_superuser` flag with **roles** and **permissions**.
- Seed three roles: **admin** (full access to user management and settings), **manager** (can list users and view metrics, but not manage users or settings), and **member** (self-service only — own profile and basic app features; default for new and self-registered accounts).
- Enforce permissions on sensitive FastAPI routes via a reusable dependency, not scattered boolean checks.
- Expose the current user's role and permission list on `/users/me` so the React app can hide routes, nav, and controls.
- Add a minimal "metrics/insights" surface (a stub page and endpoint) as a second protected feature beyond user management, to prove the permission model generalizes beyond one screen.
- Direct navigation to a route the current user lacks permission for shows a friendly "Access Denied" page instead of a silent redirect.
- **BREAKING**: User create/update payloads and public user schemas drop `is_superuser` and use a role instead. Existing superusers migrate to the admin role; everyone else to member.
- Existing pytest and Playwright cases that assume `is_superuser` are updated only as needed to keep the current suite green. No new documentation site or extra test layers.
- Document the authorization approach and permission matrix in a new `docs/AUTHORIZATION.md`, with a one-line pointer from the root `README.md`.

## Capabilities

### New Capabilities

- `rbac`: Roles, permissions, assignment to users, API enforcement, and frontend gating of sensitive screens and actions.

### Modified Capabilities

- None. There are no main specs under `openspec/specs/` yet.

## Impact

- **Backend**: `User` model and schemas, Alembic migration, `app/api/deps.py`, user/item/login/utils/metrics routes, first-superuser seed in `app/core/db.py`, CRUD helpers, existing pytest fixtures and assertions.
- **Frontend**: generated OpenAPI client, admin route guard, new metrics route guard, a shared "Access Denied" page, sidebar/nav, user create/edit forms (3-way role select), settings tab logic, Playwright admin specs.
- **Docs**: new `docs/AUTHORIZATION.md` (permission matrix, approach, setup/seed/test instructions); root `README.md` gets a one-line pointer.
- **API clients**: any consumer sending or reading `is_superuser` must switch to role (and, for the current user, permissions).
- **Dependencies**: none new; stay on SQLModel, FastAPI `Depends`, and TanStack Router.
