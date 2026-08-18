# Notes for Reviewers

Supplementary context for the [Fullstack Dev Test Task](https://github.com/evios/Fullstack-Dev-Test-Task). Required deliverables are in `README.md`; this file covers scope, trade-offs, and follow-ups.

## What Was Prioritized

1. **Centralized backend policy** — `permissions.py` + `require_permission()` dependencies.
2. **Consistent frontend UX** — hidden nav, route guards, `AccessDenied` component.
3. **Focused tests** — eight authorization scenarios (allow + deny paths), including denial logging.
4. **Runnable setup** — Docker Compose, seed users, migration, smoke script.

## Scope Cuts (and Why)

| Cut | Reason |
|-----|--------|
| E2E Playwright tests for RBAC | Backend tests + manual smoke cover critical paths within timebox |
| `/me/permissions` API | Small static matrix; mirroring in frontend is simpler (see ADR 002) |
| Row-level / resource ownership rules | Assignment surface is role-based, not object-level ACL |
| Regenerating OpenAPI client for `role` | Patched `types.gen.ts` manually; `generate-client.sh` needs running stack |

## Trade-offs

- **`is_superuser` kept in sync with `role`** — Template compatibility; admin maps to `role=admin` in CRUD layer.
- **Frontend permission duplication** — Acceptable for three roles; would generate or fetch capabilities in a larger system.

## Observability

Denied authorization attempts are logged at `WARNING` from `app.api.deps` with user id, email, role, and requested permission or required roles. Useful for audit trails and debugging mistaken 403 responses.

## With More Time

- Add Playwright flows: login as member → direct `/admin` → see Access Denied.
- Expose read-only permissions in OpenAPI and regenerate the frontend client.
- Structured audit log table for denied access (not only application logs).
- Feature flags or admin UI to assign roles without DB access.

## Architecture Docs

- ADRs: `docs/adr/001-permission-based-rbac.md`, `docs/adr/002-frontend-permission-mirror.md`
- Auth flow diagram: `README.md` (Mermaid)
