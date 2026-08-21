## Context

See proposal.md for motivation. Today authorization is a boolean `User.is_superuser` checked in `get_current_active_superuser` and inline in item and self-delete routes. The React app copies that flag for admin route `beforeLoad`, sidebar, user forms, and settings tabs. First-run seed in `app/core/db.py` creates a superuser. No authorization library is in use.

Constraints: stay on SQLModel + FastAPI `Depends` + TanStack Router; prefer a small, copy-paste-friendly model over a policy engine; keep existing pytest/Playwright green rather than adding a new test layer.

## Goals / Non-Goals

**Goals:**

- Single permission check API on the backend (`require_permission("users:list")`) replacing `is_superuser`.
- A small, realistic protected surface — list users, create a user, view a metrics/insights page, view/update your own profile — enforced identically on the backend and the frontend.
- Three roles (`admin`, `manager`, `member`) whose grants are obvious from one table, so a teammate understands the authorization model in under 5 minutes.
- Data model that can grow (new permission codes, extra seeded roles) without another boolean column or touching every route.

**Non-Goals:**

- Custom role/permission CRUD APIs or an admin UI to invent roles at runtime.
- Multi-role users, groups, tenants, or resource ACLs beyond existing item ownership.
- Casbin, Oso, or other policy engines.
- New documentation site or a dedicated unit-test framework for RBAC.

## Decisions

### 1. User has exactly one role; roles have many permissions

```
┌──────────┐     role_id      ┌──────────┐
│   User   │─────────────────▶│   Role   │  slug unique (admin, manager, member)
└──────────┘                  └────┬─────┘
                                   │
                            link table
                                   │
                              ┌────▼─────┐
                              │Permission│  code unique (users:list)
                              └──────────┘
```

**Why:** Classic RBAC, easy to reason about in a template, one FK on `user`. Many-to-many users↔roles adds join complexity without a product need. A permission enum on the user skips roles and cannot group privileges. Adding a fourth role later is one seed-data row plus a grants entry, not a new column or a new set of route checks.

**Alternatives:** Keep `is_superuser` and add extra booleans — rejected (does not scale past two tiers). Library-based RBAC — rejected (heavier than the template).

### 2. Five permission codes cover the whole surface

```
users:list      list all users / view a user other than yourself
users:create    create a user
users:manage    update or delete a user other than yourself
metrics:view    view the metrics/insights page
system:admin    everything else admin-only: item access across owners,
                transactional-email test/preview, blocks self-delete
```

| Role      | users:list | users:create | users:manage | metrics:view | system:admin |
|-----------|:---:|:---:|:---:|:---:|:---:|
| `admin`   | ✓ | ✓ | ✓ | ✓ | ✓ |
| `manager` | ✓ |   |   | ✓ |   |
| `member`  |   |   |   |   |   |

Viewing/updating your **own** profile needs no permission check — it's the baseline for any authenticated, active user, matching how `PATCH /users/me` already worked.

**Why:** The proposal's permission matrix maps directly to 4 of these codes (`users:list`, `users:create`, `users:manage`, `metrics:view`). Everything the old design protected that isn't in that matrix (item ownership bypass, test-email, password-recovery HTML preview, the "admins can't self-delete" rule) is folded into one `system:admin` code rather than kept as separate codes (`items:read_any`, `items:write_any`, `system:ops`, `users:write`). One admin-only catch-all is easier to hold in your head than four overlapping ones, and it's still just a `require_permission("system:admin")` call at each of those sites — nothing about the dependency mechanism changes.

**Alternatives:** Keep the old finer-grained codes alongside the three new ones (8 total) — rejected, adds surface area without adding real access control (nothing but `admin` was ever going to hold the fine-grained ones). Drop those protections entirely — rejected, it's a behavior regression nobody asked for.

### 3. FastAPI dependency factory, not a new middleware

`require_permission(code: str)` returns a dependency that loads the current user, resolves permission codes for their role, and raises 403 if `code` is missing. Item ownership stays in the item routes: missing `system:admin` falls back to `owner_id == current_user.id` (same shape as today's superuser bypass, inverted).

Replace `get_current_active_superuser` entirely.

**Why:** Fits existing `Annotated` / `Depends` style. Middleware would run on every route and still need per-route metadata.

### 4. `/users/me` is the UI source of truth

Extend the current-user response with `role: str` and `permissions: list[str]`. Other user list/detail payloads include `role` only (no permission dump). Frontend: small helper `hasPermission(user, code)` used by sidebar, admin `beforeLoad`, the new metrics route guard, and settings tab filtering. A `PERMISSIONS` constants object in the frontend mirrors the backend's codes so call sites never hardcode strings. Regenerated OpenAPI client after schema change.

**Why:** UI must not invent a second mapping from role slug → screens. Listing other users' full permission sets is unnecessary.

### 5. Breaking replacement of `is_superuser`

Drop the column. User create/update take `role` slug (optional on create, default `member`). Admin forms: role select (`member` | `manager` | `admin`) instead of "Is superuser?".

Self-delete guard: if the current user has `system:admin`, forbid self-delete (same intent as "superusers cannot delete themselves").

**Why:** Dual-writing `is_superuser` and roles would keep the problem the change is meant to remove.

### 6. Metrics/insights page is a stub

Backend: `GET /api/v1/metrics/`, gated on `metrics:view`, returns a small fixed/derived payload (e.g. user and item counts) — not a real analytics pipeline. Frontend: one route (`/metrics`) with a placeholder page, gated the same way the admin route is, plus a sidebar nav item shown only when `metrics:view` is granted.

**Why:** The clarification explicitly says "simple stub is acceptable" — this exists to prove the permission model covers a second, non-user-management feature, not to build real analytics.

### 7. Direct navigation to a forbidden route shows Access Denied, not a silent bounce

Add one shared `AccessDenied` page component and a `/forbidden` route. Route `beforeLoad` guards (admin, metrics) redirect there — with the attempted path preserved for the message — instead of silently redirecting to `/`. The sidebar still hides nav items the user can't use; Access Denied only fires when someone lands on a guarded URL directly (typed, bookmarked, or a stale link).

**Why:** A silent redirect to `/` looks like a bug ("why did my click do nothing?"); a cryptic 403 JSON blob is worse. One reusable component keeps this consistent across every guarded route without duplicating the message in each one — adding a fourth guarded route later is "call the same guard, done," not "invent new copy."

**Alternatives:** Show nothing and redirect silently (today's behavior) — rejected, fails the "no cryptic/silent failures" requirement. Render the denial inline per-route — rejected, duplicates copy and styling across every guarded route.

### 8. Documentation lives in one dedicated file, not scattered comments

Permission matrix, the 2-4 paragraph approach explanation (where checks live, how roles are stored/validated, how the frontend learns capabilities), and setup/seed/test-run instructions go in a new `docs/AUTHORIZATION.md`. The root `README.md` (template-wide, not RBAC-specific) gets a single pointer line rather than a large inserted section. Code itself stays comment-free except where the *why* genuinely isn't obvious from structure — e.g. one line on `require_permission` explaining it's a dependency factory (not a dependency itself), and one line on the `system:admin` catch-all explaining why several unrelated checks share one code (see design decision 2). No comment restates what a role/permission constant already says.

**Why:** Matches the rubric's own split — code should be self-documenting via naming and structure; a dedicated doc is for the matrix and the "why," not a substitute for readable code, and not bolted onto an already-large template README.

### 9. Tests: a few well-chosen backend cases beat exhaustive matrix coverage

One pytest test per meaningfully distinct authorization path — not one per matrix cell. Concretely: an allowed and a denied case for each of `users:list`, `users:create`, `users:manage`, `metrics:view`; one case proving "update your own profile" needs no permission; one case proving a `member` cannot escalate their own role via the self-update endpoint (since `UserUpdateMe` has no `role` field, this is a schema-level guarantee worth asserting explicitly, not just trusting the type). That's roughly 8-10 focused, clearly named tests, not a 3×5 role×permission grid. Playwright coverage stays limited to what already existed (admin/login specs) plus asserting the Access Denied page renders for one blocked route — not a full frontend permission matrix.

**Why:** The rubric explicitly rewards "3 well-chosen tests with clean code" over a large sprawling suite, and privilege-escalation-via-self-update is the one non-obvious gap worth a dedicated test rather than trusting "the schema doesn't have the field" to be self-evident.

## Risks / Trade-offs

- [Stale UI if permissions change while a session is open] → Accept for v1; `/users/me` is already fetched on layout. Document that a refresh picks up role changes.
- [Forgotten route still using `is_superuser`] → Grep during apply; remove the field so type-checkers fail.
- [Admin with empty permission table if seed skipped] → `init_db` upserts permissions every startup, not only when the first user is created.
- [One role per user is inflexible] → Accept; adding a link table later is possible without changing permission codes.
- [`system:admin` bundles unrelated concerns (items, email, self-delete) behind one code] → Accepted trade-off for a small, understandable surface; only `admin` ever holds it today, so splitting it later (if a role needs items-bypass but not email-preview) is a non-breaking migration — add a code, update the seed grants, update the two or three call sites that used the bundled one.

## Migration Plan

This change has not shipped yet, so the RBAC migration already written for the two-role version is **rewritten in place** rather than stacked with a second migration — there is no production data depending on the old `admin`/`user` seed to preserve.

1. Add `permission`, `role`, `role_permission` tables and nullable `user.role_id`.
2. Seed `admin`, `manager`, `member` roles and the five permission codes (same codes as `init_db`) with the grants table above.
3. `UPDATE` users: `is_superuser = true` → `admin`, else → `member`.
4. Make `role_id` NOT NULL; drop `is_superuser`.
5. Deploy backend then regenerate frontend client.

Rollback: reverse migration restores `is_superuser` from `role.slug == 'admin'`. In-flight tokens remain valid (user id in JWT is unchanged).
