# ADR 002: Mirror Permissions on the Frontend for UX Only

## Status

Accepted

## Context

The backend must enforce RBAC on every sensitive endpoint. The frontend still needs to hide sidebar links, block direct URL navigation, and show a friendly "Access Denied" state instead of empty screens or cryptic API errors.

Options: fetch capabilities from the API, derive UI state from JWT claims only, or duplicate the permission matrix client-side.

## Options Considered

1. **Dedicated `/me/permissions` endpoint** — Single source of truth at runtime; extra API surface and caching considerations.
2. **JWT custom claims with permission list** — Avoids an extra round-trip but couples token size and refresh to policy changes.
3. **Mirror the backend matrix in TypeScript** — Same `Permission` strings and role map as `permissions.py`; UI checks are synchronous.

## Decision

Use **option 3**: `frontend/src/lib/permissions.ts` mirrors `backend/app/core/permissions.py`. The `usePermissions()` hook reads the logged-in user's `role` from existing auth state and gates navigation and route components.

The backend remains authoritative. A user who bypasses the UI still receives HTTP `403` from the API.

## Consequences

**Pros**

- No new endpoints or token format changes.
- Sidebar and route guards work offline from cached user profile data already loaded after login.
- `AccessDenied` gives clear UX for direct navigation to forbidden routes.

**Cons**

- Two places must stay in sync when permissions change (documented in README; tests cover backend; smoke script covers API).
- Role changes after login are not reflected until the user re-authenticates or refetches profile.

## Trade-offs

For this task, duplication is acceptable because the matrix is small and stable. With more roles or dynamic permissions, we would add a capabilities endpoint or generate shared types from OpenAPI/schema.
