---
title: "API Overview"
doc-type: reference
status: active
version: "1.5.0"
base-url: "/api/v1"
last-updated: 2026-02-28
updated-by: "api-docs-writer (AYG-71)"
related-code:
  - backend/app/main.py
  - backend/app/api/main.py
  - backend/app/api/deps.py
  - backend/app/api/routes/entities.py
  - backend/app/api/routes/health.py
  - backend/app/models/entity.py
  - backend/app/services/entity_service.py
  - backend/app/core/config.py
  - backend/app/core/security.py
  - backend/app/core/errors.py
related-docs:
  - docs/architecture/overview.md
  - docs/data/models.md
tags: [api, rest, overview]
---

# API Overview

## Base Information

| Property | Value |
|----------|-------|
| Base URL | `http://localhost:8000/api/v1` |
| Authentication | Clerk JWT (Bearer token) |
| Content Type | `application/json` |
| API Version | 1.1.0 |
| OpenAPI Spec | `GET /api/v1/openapi.json` |
| Swagger UI | `GET /docs` |
| ReDoc | `GET /redoc` |

## Authentication

> **AYG-65:** Authentication has migrated from an internal HS256 JWT to **Clerk JWT**. The `/login/access-token` password-flow endpoint is deprecated as part of this migration (see [Login & Authentication](endpoints/login.md)).

The API uses Clerk-issued JWT bearer tokens. Clients obtain a token directly from Clerk (via the Clerk SDK or Clerk-hosted UI), then pass it to the API on every request.

### Auth Flow

1. Client authenticates with Clerk (hosted UI, SDK sign-in, or OAuth provider).
2. Clerk issues a short-lived JWT signed with Clerk's RSA key.
3. Client sends the JWT as a `Bearer` token in the `Authorization` header.
4. FastAPI dependency verifies the token via the Clerk SDK and extracts a `Principal` (containing `user_id`, `roles`, and `org_id`).
5. The resolved `Principal` is forwarded to route handlers for authorization decisions.

### Using a Token

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <clerk_jwt>" \
  -H "Content-Type: application/json"
```

### Principal Claims

After verification the Clerk SDK exposes the following fields to route handlers:

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Clerk user identifier (e.g. `user_2abc...`) |
| `roles` | array[string] | Roles assigned in the Clerk organization session |
| `org_id` | string \| null | Active organization identifier, if the session is org-scoped |

### Token Lifetime

Token expiry is controlled by Clerk session settings. Clients should treat tokens as short-lived and use Clerk's SDK refresh mechanisms rather than storing or re-using tokens long-term.

## Endpoint Summary

Endpoints are grouped by resource. **Operational endpoints** (`/healthz`, `/readyz`, `/version`) are mounted at the **root level** — they are not under `/api/v1`. All other paths are relative to the base URL `/api/v1`.

### Operational Endpoints (Root Level)

These endpoints are public (no authentication required) and mounted directly on the application root for compatibility with container orchestrators and API gateways. They do not appear in the `/api/v1/openapi.json` spec.

| Method | Path | Description | Auth Required |
|--------|------|-------------|:-------------:|
| `GET` | `/healthz` | Liveness probe — returns `{"status": "ok"}` immediately | No |
| `GET` | `/readyz` | Readiness probe — checks Supabase connectivity | No |
| `GET` | `/version` | Build metadata for API gateway service discovery | No |

> **Note:** `/readyz` returns `200` when all checks pass and `503` when any dependency is unreachable. Container orchestrators (Kubernetes, ECS) use these distinct status codes to gate traffic routing. `/healthz` always returns `200` regardless of dependency state.

### Entities

> **Active (AYG-70):** Entity CRUD endpoints are implemented and registered at `/api/v1/entities`. See [Entities API](endpoints/entities.md) for full documentation.

All entity endpoints are scoped to the authenticated caller — `owner_id` isolation is enforced at the service layer, so users can only access their own records.

| Method | Path | Description | Auth Required |
|--------|------|-------------|:-------------:|
| `POST` | `/entities` | Create a new entity | Yes |
| `GET` | `/entities` | List caller's entities (paginated, max 100 per page) | Yes |
| `GET` | `/entities/{entity_id}` | Get a single entity by UUID | Yes |
| `PATCH` | `/entities/{entity_id}` | Partially update an entity | Yes |
| `DELETE` | `/entities/{entity_id}` | Delete an entity (returns 204) | Yes |

## Standard Response Patterns

### Pagination

List endpoints return a `PaginatedResponse[T]` envelope and accept `offset` and `limit` query parameters:

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `offset` | integer | `0` | — | Number of records to skip |
| `limit` | integer | `20` | `100` | Maximum records to return per page |

> **Note:** Some existing endpoints still use the legacy `skip` parameter name; these will be renamed to `offset` during the AYG-65 migration cycle. Both names are accepted in the transition period.

`PaginatedResponse[T]` shape:

```json
{
  "data": [...],
  "count": 42
}
```

`data` is an array of the resource type `T`; `count` is the **total** number of matching records in the system (not just the current page), useful for building pagination controls.

### Date / Time

All timestamp fields (e.g. `created_at`) are returned in **UTC ISO 8601** format:

```
2026-02-24T12:34:56.789012+00:00
```

### UUIDs

All resource identifiers (`id`, `owner_id`, `user_id`) are version-4 UUIDs:

```
550e8400-e29b-41d4-a716-446655440000
```

## Data Models

### Message

Returned by endpoints that perform an action with no resource to return (e.g. delete, password change).

```json
{
  "message": "Item deleted successfully"
}
```

## Standard Error Responses

> **AYG-65 / AYG-71:** All API errors return a unified JSON shape applied to every active endpoint. The previous `{"detail": "..."}` format is no longer used. Every `HTTPException`, `RequestValidationError`, and unhandled `Exception` goes through `backend/app/core/errors.py` and produces the structure below. As of AYG-71 only `/api/v1/entities` and the root-level operational endpoints (`/healthz`, `/readyz`, `/version`) are registered; all legacy routes (login, users, items, utils, private) have been removed from the router.

### Standard Error Shape

Every error response (4xx and 5xx) returns JSON with these top-level fields:

```json
{
  "error": "NOT_FOUND",
  "message": "The requested user does not exist.",
  "code": "ENTITY_NOT_FOUND",
  "request_id": "a3f1c2d4-1234-5678-abcd-ef9876543210"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `error` | string | High-level error category derived from the HTTP status code (see table below) |
| `message` | string | Human-readable description of what went wrong |
| `code` | string | Machine-readable sub-code for programmatic handling (e.g. `ENTITY_NOT_FOUND`) |
| `request_id` | string (UUID v4) | Unique identifier for this request; matches the `X-Request-ID` response header for log correlation |

### HTTP Status to Error Category Mapping

| HTTP Status | `error` value | Common Cause |
|-------------|---------------|--------------|
| `400` | `BAD_REQUEST` | Invalid input or business rule violation |
| `401` | `UNAUTHORIZED` | Missing or malformed `Authorization` header |
| `403` | `FORBIDDEN` | Token is invalid, expired, or caller lacks privileges |
| `404` | `NOT_FOUND` | Requested resource does not exist |
| `409` | `CONFLICT` | Resource state conflict (e.g. duplicate email) |
| `422` | `VALIDATION_ERROR` | Request body or query parameter validation failed |
| `429` | `RATE_LIMITED` | Too many requests |
| `500` | `INTERNAL_ERROR` | Unexpected server-side failure |
| `503` | `SERVICE_UNAVAILABLE` | Upstream dependency unavailable |

### Validation Error Extension (422)

When request validation fails (HTTP 422), the response extends the standard shape with a `details` array containing per-field information:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "code": "VALIDATION_FAILED",
  "request_id": "a3f1c2d4-1234-5678-abcd-ef9876543210",
  "details": [
    {
      "field": "title",
      "message": "Field required",
      "type": "missing"
    },
    {
      "field": "email",
      "message": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

Each entry in `details`:

| Field | Type | Description |
|-------|------|-------------|
| `field` | string | Dot-notation path to the invalid field (e.g. `address.postcode`); `"unknown"` if the location cannot be determined |
| `message` | string | Validation failure description |
| `type` | string | Pydantic error type identifier (e.g. `missing`, `value_error`, `string_too_short`) |

### Request ID

The `request_id` in every error response is a UUID v4 that is also echoed back in the `X-Request-ID` response header. Use this value when filing bug reports or searching application logs.

## CORS

CORS allowed origins are controlled by two configuration values:

| Setting | Default | Description |
|---------|---------|-------------|
| `BACKEND_CORS_ORIGINS` | `[]` | Comma-separated list or JSON array of additional allowed origins |
| `FRONTEND_HOST` | `http://localhost:5173` | Always appended to the allowed origins list |

## Environment-Specific Behaviour

| Feature | `local` | `staging` | `production` |
|---------|---------|-----------|--------------|
| Default secret key warning | Warning logged | Error raised | Error raised |
| Sentry error tracking | Optional | Configured via `SENTRY_DSN` | Configured via `SENTRY_DSN` |

## Rate Limiting

<!-- TODO: Populate when rate limiting is implemented -->
[placeholder]

## Related

- [Architecture Overview](../architecture/overview.md)
- [Data Models](../data/models.md)
- [Getting Started](../getting-started/)

## Endpoint Reference

- [Operational Endpoints — Health, Readiness, Version](endpoints/health.md)
- [Entities](endpoints/entities.md)

> **Removed in AYG-71:** Login, Users, Items, Utils, and Private routes have been removed from the router. Their documentation files are retained for historical reference with a `status: deprecated` marker.

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.5.0 | 2026-02-28 | AYG-71: Legacy routes (login, users, items, utils, private) removed from router; only /api/v1/entities and root operational endpoints active; unified error shape confirmed applied to all active endpoints |
| 1.4.0 | 2026-02-28 | AYG-70: Entity CRUD route handlers registered; all five endpoints live |
| 1.3.0 | 2026-02-28 | AYG-69: Entity resource forward-reference added; service layer complete, routes planned for AYG-70 |
| 1.2.0 | 2026-02-28 | AYG-68: Operational endpoints (`/healthz`, `/readyz`, `/version`) added at root level; Utils `/health-check/` marked as legacy |
| 1.1.0 | 2026-02-27 | AYG-65: Auth updated to Clerk JWT; unified error response shape documented; `PaginatedResponse[T]` and `offset`/`limit` pagination params documented |
| 1.0.0 | 2026-02-26 | Initial release |
