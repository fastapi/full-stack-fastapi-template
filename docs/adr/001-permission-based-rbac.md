# ADR 001: Permission-Based RBAC Instead of Inline Role Checks

## Status

Accepted

## Context

The assignment requires three roles (`admin`, `manager`, `member`) and a small but realistic authorization surface (users, metrics, profile, settings). Routes could check roles directly (`if user.role == UserRole.ADMIN`) or go through a shared permission layer.

We need a model that is easy to read in code review, easy to extend when a fourth role appears, and consistent between backend routes.

## Options Considered

1. **Inline role checks in each route** — Simple for three roles, but scatters policy across handlers and makes the permission matrix implicit.
2. **Permission enum + role-to-permission map** — One module defines `Permission` and `ROLE_PERMISSIONS`; routes depend on `require_permission(...)`.
3. **External policy engine (e.g. Casbin)** — Flexible for large systems, but heavy for a timeboxed task and adds a dependency.

## Decision

Use **option 2**: a central `permissions.py` with a `Permission` enum and `ROLE_PERMISSIONS` mapping. FastAPI dependencies in `deps.py` expose `require_permission(...)` used by route handlers.

## Consequences

**Pros**

- Adding a permission or adjusting a role touches one map and route dependencies, not every `if role == ...` branch.
- The matrix in README maps directly to `Permission` values and tests.
- Reviewers can understand policy in one file within a few minutes.

**Cons**

- Frontend duplicates the matrix in `permissions.ts` (see ADR 002).
- Fine-grained rules beyond the static matrix (e.g. row-level access) would need extra helpers; not required for this task.

## Trade-offs

We deliberately avoided a policy engine to keep scope tight. For production at scale, we would evaluate syncing permissions from the API or adopting a dedicated authorization service.
