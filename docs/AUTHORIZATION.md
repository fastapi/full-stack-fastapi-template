# Authorization

This project uses role-based access control (RBAC): every user has exactly one role, and each role grants a fixed set of permission codes. Routes and UI check permission codes, never role names.

## Permission matrix

| Action                          | admin | manager | member |
|----------------------------------|:-----:|:-------:|:------:|
| List all users                   |   ✓   |    ✓    |   ✗    |
| Create a user                    |   ✓   |    ✗    |   ✗    |
| View metrics/insights            |   ✓   |    ✓    |   ✗    |
| View / update **own** profile    |   ✓   |    ✓    |   ✓    |
| Update / delete **any** profile  |   ✓   |    ✗    |   ✗    |
| Access items you don't own; test-email; password-recovery preview; self-delete blocked | ✓ | ✗ | ✗ |

The five underlying permission codes are `users:list`, `users:create`, `users:manage`, `metrics:view`, and `system:admin` — the last one is a single admin-only catch-all covering the bottom row (item access across owners, transactional-email endpoints, and the rule that blocks an admin from deleting their own account). Viewing and updating your own profile needs no permission at all; it's the baseline for any authenticated, active user regardless of role.

## How it works

**Backend.** Authorization checks live in one FastAPI dependency, `require_permission(code)` (`backend/app/api/deps.py`), applied per-route via `dependencies=[Depends(require_permission(...))]`. It's a dependency *factory* — calling it with a permission code returns the actual dependency FastAPI runs. The one exception is item ownership, which stays inline in `app/api/routes/items.py` as a fallback (`owner_id == current_user.id`) because it's data-scoped, not role-scoped. There is no middleware and no decorator — every protected route says explicitly, in one line, which permission it needs.

**Data model.** Roles and permissions are database tables (`role`, `permission`, `role_permission`), linked from `user.role_id`. The permission codes themselves and the role→permission grants are defined once, as plain Python constants, in `backend/app/core/rbac.py` — that file is the single source of truth. `init_db` (`backend/app/core/db.py`) upserts this seed data on every startup, so the roles and grants in the database always match the constants in code. Adding a new role is one entry in the seed data plus one line in `rbac.py`'s `ROLE_PERMISSIONS` mapping; adding a new permission is one constant plus wiring it into the roles and routes that need it — neither requires touching every route.

**Frontend.** The frontend never re-derives permissions from a role name. `GET /users/me` returns the current user's role slug and their full list of permission codes; the frontend stores that on the authenticated user object and checks it with one helper, `hasPermission(user, code)` (`frontend/src/utils.ts`), mirrored against a `PERMISSIONS` constants object with the same five codes. Every gated nav item, route guard, and form control calls that helper — never `user.role === "..."`. Route guards that fail redirect to a shared `/forbidden` page (`AccessDenied` component) rather than silently bouncing to `/` or showing a blank screen, so a user who follows a stale link or bookmark gets an explicit, friendly explanation instead of a mystery.

## Setup

Requirements: [Docker](https://www.docker.com/), [uv](https://docs.astral.sh/uv/), [Bun](https://bun.sh/). See the root [`development.md`](../development.md) for the full local-dev workflow; the RBAC-relevant steps are below.

1. Start Postgres and Mailpit from the project root:

   ```bash
   docker compose up -d db mailpit
   ```

2. From `backend/`, install dependencies, run migrations, and seed the database (this also creates the first admin — see below):

   ```bash
   uv sync
   uv run bash scripts/prestart.sh
   uv run fastapi dev
   ```

3. From the project root, install and start the frontend:

   ```bash
   bun install
   bun run dev
   ```

   Frontend: <http://localhost:5173>. Backend: <http://localhost:8000> (docs at `/docs`).

### Seeding an admin and a non-admin account

`scripts/prestart.sh` already seeds the `admin`, `manager`, and `member` roles with their permission grants, and creates one `admin` account from the `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD` values in `.env` (defaults: `admin@example.com` / `changethis`).

To get a non-admin account for manual testing, either self-register through the UI or `POST /api/v1/users/signup` (always creates a `member`), or have an existing admin create one with a specific role — e.g. from `backend/`:

```console
$ uv run python -c "
from sqlmodel import Session
from app.core.db import engine
from app.models import UserCreate
from app import crud

with Session(engine) as session:
    crud.create_user(session=session, user_create=UserCreate(
        email='manager@example.com', password='password123', role='manager',
    ))
"
```

(`role` accepts `admin`, `manager`, or `member`; omit it to get the `member` default.)

## Running tests

Backend (from `backend/`):

```bash
uv run bash scripts/test.sh
```

Frontend/Playwright (from `frontend/`, requires the stack running):

```bash
bunx playwright test
```

## Migrations

Standard Alembic workflow — see [`backend/README.md`](../backend/README.md#migrations). The RBAC schema (roles, permissions, `user.role_id`) is introduced in `backend/app/alembic/versions/2d1ae9889b29_add_rbac_roles_and_permissions.py`, which also seeds the roles/permissions and backfills existing users' roles.
