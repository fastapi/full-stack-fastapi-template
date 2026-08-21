## 1. Data model and migration rework

- [x] 1.1 Rewrite (in place, not stacked — unshipped) migration `2d1ae9889b29`: seed roles `admin`/`manager`/`member` and permission codes `users:list`, `users:create`, `users:manage`, `metrics:view`, `system:admin`; grant admin all five, manager `users:list`+`metrics:view`, member none; backfill `is_superuser=true` → `admin`, else → `member`. Verify `alembic upgrade head` succeeds against a DB that previously had superusers, and role/permission rows match the grants table.
- [x] 1.2 Update `app/core/rbac.py` constants (`ROLE_ADMIN`/`ROLE_MANAGER`/`ROLE_MEMBER`, the five permission codes, `ROLE_PERMISSIONS`) to the new model. Verify constants match design.md's grants table exactly.

## 2. Backend authorization remap

- [x] 2.1 Remap `require_permission()` call sites: user list / get-other-user → `users:list`; user create → `users:create`; user update/delete-other → `users:manage`; item any-owner access, test-email, password-recovery-html-content → `system:admin`. Verify a `manager` gets 200 on list-users and 403 on create-user; a `member` gets 403 on both.
- [x] 2.2 Update the self-delete guard (`DELETE /users/me`) to block on `system:admin` instead of the old `users:write`. Verify admin self-delete still returns 403 and manager/member self-delete succeeds.
- [x] 2.3 Add `GET /api/v1/metrics/` stub endpoint gated on `metrics:view`, returning a small fixed/derived payload. Verify `admin` and `manager` get 200, `member` gets 403.
- [x] 2.4 Security pass: confirm `UserUpdateMe` has no `role` field (self-update cannot escalate privilege) and grep for any remaining direct `role`/permission-code checks that bypass `require_permission`/`has_permission`. Add the one non-obvious clarifying comment each on `require_permission` (it's a dependency *factory*) and the `system:admin` catch-all (why several unrelated checks share one code) — no other authorization comments.

## 3. Frontend remap and Access Denied UX

- [x] 3.1 Regenerate the OpenAPI client (schema now includes the metrics route). Update the `PERMISSIONS` constants object in `src/utils.ts` to the five new codes.
- [x] 3.2 Add a shared `AccessDenied` page component and a `/forbidden` route. Update the admin and metrics route `beforeLoad` guards to redirect there (not to `/`) when the permission check fails.
- [x] 3.3 Update sidebar gating from the old codes to `users:list`; add a "Metrics" nav item and `/metrics` route guarded by `metrics:view` with a stub page. Verify a `member` sees neither Admin nor Metrics nav items, and direct navigation to either route shows the Access Denied page (not a silent redirect); a `manager` sees and can open both.
- [x] 3.4 Replace the two-way role select in Add/Edit User forms with a three-way select (`member` | `manager` | `admin`). Verify creating/editing a user with each role persists correctly and the users table shows the right role badge.
- [x] 3.5 Update the settings danger-zone tab gating from the old `users:write` check to `system:admin`. Verify only `admin` sessions hide the self-delete tab; `manager` and `member` still see it.

## 4. Documentation

- [x] 4.1 Write `docs/AUTHORIZATION.md`: permission matrix (role × permission, matching design.md's grants table); a 2-4 paragraph approach explanation covering where checks live (the `require_permission` dependency, not middleware/decorators), how roles are stored and validated (the `role`/`permission`/`role_permission` tables plus `rbac.py` constants), and how the frontend learns capabilities (`/users/me`'s `permissions` array plus the `hasPermission` helper). Add a one-line pointer to it from the root `README.md`.
- [x] 4.2 Add setup/seed/test-run instructions to `docs/AUTHORIZATION.md`: how to run the app locally, how to seed at least one admin and one non-admin (manager or member) account for manual testing, how to run `alembic upgrade head`, and how to run the backend and frontend test suites.

## 5. Existing tests

- [x] 5.1 Update pytest fixtures/assertions for the new role slugs and permission codes. Write a small, focused set of new authorization tests (not an exhaustive per-cell matrix) covering: an allowed and a denied case for each of `users:list`, `users:create`, `users:manage`, `metrics:view`; that any authenticated user can update their own profile without a permission; and that a `member` cannot escalate their own role via the self-update endpoint. Verify `pytest` in `backend/` passes.
- [x] 5.2 Update Playwright admin specs for the new role terminology and the three-way role select; add one assertion that navigating a `member` session directly to a guarded URL renders the Access Denied page. Verify `bunx playwright test` admin/login specs still pass.
