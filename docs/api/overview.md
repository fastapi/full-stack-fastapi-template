---
title: "API Overview"
doc-type: reference
status: draft
version: "1.0.0"
base-url: "/api/v1"
last-updated: 2026-02-26
updated-by: "initialise skill"
related-code:
  - backend/app/api/main.py
  - backend/app/api/deps.py
  - backend/app/api/routes/login.py
  - backend/app/api/routes/users.py
  - backend/app/api/routes/items.py
  - backend/app/api/routes/utils.py
  - backend/app/api/routes/private.py
  - backend/app/models.py
  - backend/app/core/config.py
  - backend/app/core/security.py
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
| Authentication | OAuth2 Bearer token (JWT HS256) |
| Content Type | `application/json` |
| API Version | 1.0.0 |
| OpenAPI Spec | `GET /api/v1/openapi.json` |
| Swagger UI | `GET /docs` |
| ReDoc | `GET /redoc` |

## Authentication

The API uses OAuth2 with JWT bearer tokens. Tokens are signed using the HS256 algorithm and expire after 8 days (11,520 minutes).

### Obtaining a Token

Submit credentials as `application/x-www-form-urlencoded` (OAuth2 password flow):

```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using a Token

Include the token in the `Authorization` header for all protected endpoints:

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json"
```

### Token Payload

JWT tokens contain the following claims:

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string (UUID) | The authenticated user's ID |
| `exp` | integer (Unix timestamp) | Token expiry time |

### Password Hashing

Passwords are hashed using `pwdlib` with Argon2 as the primary hasher and Bcrypt as the fallback. Plain-text passwords are never stored.

## Endpoint Summary

Endpoints are grouped by resource. All paths are relative to the base URL `/api/v1`.

### Auth / Login

| Method | Path | Description | Auth Required | Superuser |
|--------|------|-------------|:-------------:|:---------:|
| `POST` | `/login/access-token` | Obtain a JWT access token (OAuth2 password flow) | No | No |
| `POST` | `/login/test-token` | Validate an access token and return the current user | Yes | No |
| `POST` | `/password-recovery/{email}` | Send a password reset email | No | No |
| `POST` | `/reset-password/` | Reset password using a recovery token | No | No |
| `POST` | `/password-recovery-html-content/{email}` | Preview the password-reset email HTML | Yes | Yes |

### Users

| Method | Path | Description | Auth Required | Superuser |
|--------|------|-------------|:-------------:|:---------:|
| `GET` | `/users/` | List all users (paginated) | Yes | Yes |
| `POST` | `/users/` | Create a new user (admin-only) | Yes | Yes |
| `POST` | `/users/signup` | Self-register a new account | No | No |
| `GET` | `/users/me` | Get the current authenticated user | Yes | No |
| `PATCH` | `/users/me` | Update the current user's profile | Yes | No |
| `PATCH` | `/users/me/password` | Change the current user's password | Yes | No |
| `DELETE` | `/users/me` | Delete the current user's own account | Yes | No |
| `GET` | `/users/{user_id}` | Get a specific user by ID | Yes | No* |
| `PATCH` | `/users/{user_id}` | Update a specific user | Yes | Yes |
| `DELETE` | `/users/{user_id}` | Delete a specific user | Yes | Yes |

*Non-superusers can only retrieve their own record. Attempting to fetch another user's record returns `403`.

### Items

| Method | Path | Description | Auth Required | Superuser |
|--------|------|-------------|:-------------:|:---------:|
| `GET` | `/items/` | List items (all for superusers, own only for regular users) | Yes | No |
| `POST` | `/items/` | Create a new item | Yes | No |
| `GET` | `/items/{id}` | Get a specific item by ID | Yes | No |
| `PUT` | `/items/{id}` | Replace an item | Yes | No |
| `DELETE` | `/items/{id}` | Delete an item | Yes | No |

Non-superusers can only access items they own. Accessing another user's item returns `403`.

### Utils

| Method | Path | Description | Auth Required | Superuser |
|--------|------|-------------|:-------------:|:---------:|
| `GET` | `/utils/health-check/` | Liveness probe — returns `true` | No | No |
| `POST` | `/utils/test-email/` | Send a test email to a given address | Yes | Yes |

### Private (local environment only)

These endpoints are only registered when `ENVIRONMENT=local`. They bypass normal validation and are intended for development and seeding.

| Method | Path | Description | Auth Required | Superuser |
|--------|------|-------------|:-------------:|:---------:|
| `POST` | `/private/users/` | Create a user directly (no email check, no welcome email) | No | No |

## Request / Response Patterns

### Pagination

List endpoints accept `skip` and `limit` query parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | `0` | Number of records to skip |
| `limit` | integer | `100` | Maximum records to return |

Paginated responses wrap results in an envelope:

```json
{
  "data": [...],
  "count": 42
}
```

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

### UserPublic

Returned when reading or creating users.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Jane Doe",
  "created_at": "2026-02-24T12:00:00+00:00"
}
```

### UsersPublic

Returned by `GET /users/`.

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "is_active": true,
      "is_superuser": false,
      "full_name": "Jane Doe",
      "created_at": "2026-02-24T12:00:00+00:00"
    }
  ],
  "count": 1
}
```

### ItemPublic

Returned when reading or creating items.

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "My Item",
  "description": "An optional description",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-24T12:00:00+00:00"
}
```

### ItemsPublic

Returned by `GET /items/`.

```json
{
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "My Item",
      "description": "An optional description",
      "owner_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-02-24T12:00:00+00:00"
    }
  ],
  "count": 1
}
```

### Token

Returned by `POST /login/access-token`.

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Message

Returned by endpoints that perform an action with no resource to return (e.g. delete, password change).

```json
{
  "message": "Item deleted successfully"
}
```

## Error Format

FastAPI / Pydantic validation errors return the standard detail structure:

```json
{
  "detail": "Human-readable error description"
}
```

Validation errors from Pydantic (HTTP 422) return a richer format:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Common Error Codes

| HTTP Status | Description | Example Cause |
|-------------|-------------|---------------|
| `400 Bad Request` | Invalid input or business rule violation | Wrong credentials, inactive user, duplicate email, same old/new password |
| `401 Unauthorized` | Missing or malformed `Authorization` header | No bearer token provided |
| `403 Forbidden` | Token is invalid or user lacks privileges | Expired / tampered JWT, non-superuser accessing admin endpoint, superuser trying to delete themselves |
| `404 Not Found` | Requested resource does not exist | Unknown user ID or item ID |
| `409 Conflict` | Resource state conflict | Email already registered for another user |
| `422 Unprocessable Entity` | Request body / query parameter validation failed | Missing required field, value out of allowed range |
| `500 Internal Server Error` | Unexpected server-side failure | Database connectivity issue |

## CORS

CORS allowed origins are controlled by two configuration values:

| Setting | Default | Description |
|---------|---------|-------------|
| `BACKEND_CORS_ORIGINS` | `[]` | Comma-separated list or JSON array of additional allowed origins |
| `FRONTEND_HOST` | `http://localhost:5173` | Always appended to the allowed origins list |

## Environment-Specific Behaviour

| Feature | `local` | `staging` | `production` |
|---------|---------|-----------|--------------|
| Private endpoints (`/private/*`) | Enabled | Disabled | Disabled |
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

- [Login & Authentication](endpoints/login.md)
- [Users](endpoints/users.md)
- [Items](endpoints/items.md)
- [Utils](endpoints/utils.md)
