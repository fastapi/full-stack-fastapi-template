---
title: "Login & Authentication API"
doc-type: reference
status: deprecated
version: "1.2.0"
base-url: "/api/v1"
last-updated: 2026-02-28
updated-by: "api-docs-writer (AYG-71)"
related-code:
  - backend/app/api/routes/login.py
  - backend/app/api/deps.py
  - backend/app/core/security.py
  - backend/app/core/errors.py
  - backend/app/models.py
related-docs:
  - docs/api/overview.md
  - docs/architecture/overview.md
  - docs/data/models.md
tags: [api, rest, login, auth, jwt, deprecated]
---

# Login & Authentication API

> **DEPRECATED**: This endpoint was removed from the router in AYG-71. The file is retained for historical reference only.

> **DEPRECATED — AYG-65**
>
> This router covers the internal OAuth2 password-flow login that issued HS256-signed JWTs. As part of the Supabase + Clerk migration (AYG-65 through AYG-74), **authentication is moving to Clerk**. Clients will obtain tokens directly from Clerk's hosted UI or SDK; the `/login/access-token` endpoint is no longer the correct way to authenticate.
>
> - All endpoints in this file remain available during the migration transition period.
> - Once migration is complete, this router will be removed and this document will be archived.
> - See [API Overview — Authentication](../overview.md#authentication) for the new Clerk JWT auth flow.

## Overview

The login router handles all authentication flows for the legacy internal-JWT system: obtaining JWT access tokens via the OAuth2 password grant, validating existing tokens, and the full password-recovery cycle (request reset email, reset with token, and preview the email HTML). All paths are unprefixed and sit directly under `/api/v1`.

**Base URL:** `/api/v1`
**Authentication:** None required for most endpoints (see individual endpoint notes)
**Tag:** `login`
**Status:** Deprecated — being replaced by Clerk auth (AYG-65 through AYG-74)

## Quick Start

```bash
# Obtain a token (legacy — use Clerk SDK in new integrations)
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

---

## Endpoints

### POST /login/access-token

OAuth2 password flow — exchange credentials for a JWT access token.

**Authentication:** Not required
**Authorization:** None — public endpoint
**Content-Type:** `application/x-www-form-urlencoded` (OAuth2 form, not JSON)

**Request Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string (email) | Yes | The user's email address |
| `password` | string | Yes | The user's password |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | Signed JWT (HS256), valid for 8 days |
| `token_type` | string | Always `"bearer"` |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret1234"
```

**Example Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3NDA2NTI4MDB9.abc123",
  "token_type": "bearer"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | Credentials do not match any active user (`"Incorrect email or password"`) |
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | User account exists but `is_active` is `false` (`"Inactive user"`) |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | Missing or malformed form fields (includes `details` array) |

---

### POST /login/test-token

Validate an existing JWT and return the authenticated user's public profile.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | User identifier |
| `email` | string | User's email address |
| `is_active` | boolean | Whether the account is active |
| `is_superuser` | boolean | Whether the user has admin privileges |
| `full_name` | string \| null | User's display name |
| `created_at` | datetime \| null | UTC timestamp of account creation |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/login/test-token" \
  -H "Authorization: Bearer <access_token>"
```

**Example Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Jane Doe",
  "created_at": "2026-01-15T10:30:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Token is missing, malformed, or has an invalid signature |
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | Token belongs to a deactivated account (`"Inactive user"`) |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | Token `sub` references a deleted user |

---

### POST /password-recovery/{email}

Send a password-reset email to the given address. Always returns the same response regardless of whether the address is registered — this prevents email-enumeration attacks.

**Authentication:** Not required
**Authorization:** None — public endpoint

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | Yes | Email address to send the reset link to |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Always `"If that email is registered, we sent a password recovery link"` |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/password-recovery/user@example.com"
```

**Example Response:**

```json
{
  "message": "If that email is registered, we sent a password recovery link"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `email` path segment is not a valid email format (includes `details` array) |

> Note: If the email is not registered, no email is sent but the response is identical to the success case. This is by design.

---

### POST /reset-password/

Reset a user's password using a previously issued recovery token.

**Authentication:** Not required
**Authorization:** None — public endpoint (requires a valid recovery token)

**Request Body:**

```json
{
  "token": "string — JWT-signed password reset token from the recovery email",
  "new_password": "string — 8 to 128 characters"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `token` | string | Yes | — | Recovery token from the reset email |
| `new_password` | string | Yes | min 8, max 128 chars | The new password to set |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | `"Password updated successfully"` |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/reset-password/" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "new_password": "newSecurePass99"
  }'
```

**Example Response:**

```json
{
  "message": "Password updated successfully"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | Recovery token is expired, malformed, or does not match a registered user (`"Invalid token"`) |
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | The account associated with the token has been deactivated (`"Inactive user"`) |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `new_password` is shorter than 8 characters or body is malformed (includes `details` array) |

---

### POST /password-recovery-html-content/{email}

Preview the HTML content of the password-recovery email that would be sent to the given address. Intended for superuser debugging and email template verification.

**Authentication:** Required (Bearer token)
**Authorization:** Superuser only

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | Yes | The registered email address to generate the preview for |

**Response (200):**

- **Content-Type:** `text/html`
- Returns the full HTML body of the password-recovery email.
- Response header `subject:` contains the email subject line.

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/password-recovery-html-content/user@example.com" \
  -H "Authorization: Bearer <superuser_access_token>"
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Token is invalid or missing |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | No registered user with that email |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.2.0 | 2026-02-28 | AYG-71: Router removed; file marked deprecated — retained for historical reference |
| 1.1.0 | 2026-02-27 | AYG-65: Marked deprecated — auth migrating to Clerk JWT; all error tables updated to unified error shape |
| 1.0.0 | 2026-02-26 | Initial release |
