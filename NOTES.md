# Notes

Context and trade-offs for the RBAC implementation.

## Time Budget

The task is scoped to ≈ 1 hour. Roughly:

- ~1 hour up front was spent setting up the backend natively (Postgres, uv, alembic, seed data) because my machine ran out of disk space and Docker wasn't a workable option. That time wasn't part of the implementation work itself, but it shaped the order in which things were done.
- The implementation work followed the task's own ranking: backend RBAC first, focused tests second, README and frontend RBAC together.

## Scope Cuts

Things I intentionally did **not** do, in order of how much they cost:

1. **Separate test database.** Tests run against the development DB and wipe `User` / `Item` tables on teardown. This means the three seed users (`admin@`, `manager@`, `member@`) are removed after pytest finishes and need to be re-seeded with `uv run python -m app.initial_data`. A proper test DB (`pytest-postgresql` or a `TESTING=1` toggle in `core/db.py`) is the right fix.

2. **Architecture Decision Records (ADRs).** Listed as optional/bonus. The README's "Authorization Approach" section covers the same ground in compact prose; a formal ADR would add structure but not new information for this scope. The decision most worth an ADR is dependency factory vs. policy layer — see "Deliberate Trade-offs" below.

3. **Diagram of auth flow.** Also optional/bonus. The request flow is short enough (JWT decode → `get_current_user` → `require_role` → route handler, then `/forbidden` on 403) that prose explains it without ambiguity.

4. **Structured logging of denied attempts.** A one-liner inside `require_role` would emit a `logger.warning` on every 403, which is useful for production observability. Skipped because there's no logging convention in the template yet and adding one halfway is worse than not having it.

## Deliberate Trade-offs

These are decisions I'd make the same way again, but they deserve explicit mention:

- **`is_superuser` left in place.** The existing template uses `is_superuser` in a few places (e.g. self-delete protection on the backend, a couple of UI checks before this work). RBAC checks are now in `role`; `is_superuser` is functionally redundant but harmless, and ripping it out would touch unrelated code. Backfill in the migration ensures `is_superuser=True` users got `role='admin'`.

- **`GET /users/{user_id}` keeps inline conditional logic.** Its rule ("own profile always allowed, others admin-only") depends on a path parameter, which dependency-based checks can't see cleanly. The check lives in the route body. A policy layer would normalize this; see above.

- **Route guards (`beforeLoad`) re-fetch `/users/me`.** Each protected route makes its own call to `/users/me` rather than reading from a shared cache. React Query would normally dedupe this, but `beforeLoad` runs outside the React tree. The cost is a few extra GET requests on navigation; the alternative (a shared cached client) was more plumbing than the time budget allowed.

## What I'd Do With More Time

In rough order of value:

1. **Isolated test database** so the seed data survives test runs.
2. **One ADR** for the dependency-vs-policy-layer decision — it's the choice most likely to be revisited as the role matrix grows.
3. **Structured logging on denied attempts** (`logger.warning` inside `require_role`) so denials are observable in production.
4. **Audit `is_superuser` call-sites** and either fully replace them with `role == UserRole.ADMIN` or document the boundary explicitly.
5. **Single source of truth for the permission matrix** — either auto-generate `frontend/src/lib/auth/permissions.ts` from a manifest or move the role check into something shared.
6. **Polish the Forbidden UX** — instead of a full redirect on 403, show a toast for in-page actions (e.g. "you don't have permission to delete this user") while keeping the redirect for full-page navigation.
