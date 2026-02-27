---
title: "Users API"
doc-type: reference
status: current
version: "1.1.0"
base-url: "/api/v1"
last-updated: 2026-02-27
updated-by: "api-docs-writer (AYG-65)"
related-code:
  - backend/app/api/routes/users.py
  - backend/app/api/deps.py
  - backend/app/core/errors.py
  - backend/app/models.py
related-docs:
  - docs/api/overview.md
  - docs/architecture/overview.md
  - docs/data/models.md
tags: [api, rest, users]
---

# Users API

## Overview

The users router manages user accounts: listing, creating, reading, updating, and deleting users. It supports both superuser-level admin operations (managing any account) and self-service operations (reading and modifying the caller's own account). Public registration is available via `/users/signup` without authentication. All paths are prefixed with `/api/v1/users`.

**Base URL:** `/api/v1/users`
**Authentication:** Clerk JWT Bearer token — required for all endpoints except `/signup`
**Tag:** `users`

> **AYG-65:** Auth dependency updated from internal HS256 JWT to Clerk JWT. The client must supply a Clerk-issued token as `Authorization: Bearer <clerk_jwt>`. See [API Overview — Authentication](../overview.md#authentication) for the full flow. All error responses now use the [unified error shape](../overview.md#standard-error-responses).

## Quick Start

```bash
# Get your own profile
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"
```

---

## Endpoints

### GET /users/

List all users (paginated). Superuser only.

**Authentication:** Required (Bearer token)
**Authorization:** Superuser only

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | integer | No | `0` | Number of records to skip |
| `limit` | integer | No | `100` | Maximum records to return |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array[UserPublic] | Ordered by `created_at` descending |
| `count` | integer | Total number of users in the system |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=20" \
  -H "Authorization: Bearer <superuser_access_token>"
```

**Example Response:**

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "admin@example.com",
      "is_active": true,
      "is_superuser": true,
      "full_name": "Admin User",
      "created_at": "2026-01-01T09:00:00+00:00"
    },
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "jane@example.com",
      "is_active": true,
      "is_superuser": false,
      "full_name": "Jane Doe",
      "created_at": "2026-01-10T14:22:00+00:00"
    }
  ],
  "count": 2
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `skip` or `limit` are not valid integers (includes `details` array) |

---

### POST /users/

Create a new user account. Superuser only. Sends a welcome email if email is enabled.

**Authentication:** Required (Bearer token)
**Authorization:** Superuser only

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "securePass99",
  "is_active": true,
  "is_superuser": false,
  "full_name": "New User"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string (email) | Yes | max 255 chars, unique | User's email address |
| `password` | string | Yes | min 8, max 128 chars | Plain-text password (hashed before storage) |
| `is_active` | boolean | No | — | Defaults to `true` |
| `is_superuser` | boolean | No | — | Defaults to `false` |
| `full_name` | string \| null | No | max 255 chars | Display name |

**Response (200):**

Returns the created `UserPublic` object.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Newly assigned user identifier |
| `email` | string | User's email address |
| `is_active` | boolean | Account active status |
| `is_superuser` | boolean | Admin privilege flag |
| `full_name` | string \| null | Display name |
| `created_at` | datetime \| null | UTC creation timestamp |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <superuser_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securePass99",
    "full_name": "New User"
  }'
```

**Example Response:**

```json
{
  "id": "b3c4d5e6-f7a8-9012-bcde-f12345678901",
  "email": "newuser@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "New User",
  "created_at": "2026-02-25T08:00:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | Email is already registered |
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | Missing required fields or constraint violations (includes `details` array) |

---

### GET /users/me

Return the currently authenticated user's profile.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user

**Response (200):**

Returns the caller's `UserPublic` object.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | User identifier |
| `email` | string | Email address |
| `is_active` | boolean | Account active status |
| `is_superuser` | boolean | Admin privilege flag |
| `full_name` | string \| null | Display name |
| `created_at` | datetime \| null | UTC creation timestamp |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
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
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | Account has been deactivated |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | Token `sub` references a deleted user |

---

### PATCH /users/me

Update the authenticated user's own profile fields (`full_name` and/or `email`).

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user

**Request Body (all fields optional):**

```json
{
  "full_name": "Updated Name",
  "email": "newemail@example.com"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `full_name` | string \| null | No | max 255 chars | New display name |
| `email` | string (email) \| null | No | max 255 chars, unique | New email address |

**Response (200):**

Returns the updated `UserPublic` object.

**Example Request:**

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Jane Smith"}'
```

**Example Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Jane Smith",
  "created_at": "2026-01-15T10:30:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `409 Conflict` | `CONFLICT` | `CONFLICT` | The requested email is already in use by another account |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | Invalid email format or field length exceeded (includes `details` array) |

---

### PATCH /users/me/password

Change the authenticated user's own password.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user

**Request Body:**

```json
{
  "current_password": "oldPassword123",
  "new_password": "newPassword456"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `current_password` | string | Yes | min 8, max 128 chars | The user's current password |
| `new_password` | string | Yes | min 8, max 128 chars | The replacement password |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | `"Password updated successfully"` |

**Example Request:**

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/me/password" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "oldPassword123",
    "new_password": "newPassword456"
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
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | `current_password` does not match the stored hash |
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | `new_password` is identical to `current_password` |
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | Password shorter than 8 characters (includes `details` array) |

---

### DELETE /users/me

Delete the authenticated user's own account. Superusers cannot delete themselves through this endpoint.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user who is NOT a superuser

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | `"User deleted successfully"` |

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"
```

**Example Response:**

```json
{
  "message": "User deleted successfully"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is a superuser (superusers cannot self-delete) |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |

---

### POST /users/signup

Register a new user account without authentication. Open to the public.

**Authentication:** Not required
**Authorization:** None — public endpoint

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "securePass99",
  "full_name": "New User"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string (email) | Yes | max 255 chars, unique | Email address (used as login username) |
| `password` | string | Yes | min 8, max 128 chars | Plain-text password (hashed before storage) |
| `full_name` | string \| null | No | max 255 chars | Display name |

**Response (200):**

Returns the created `UserPublic` object. New accounts are active and non-superuser by default.

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securePass99",
    "full_name": "New User"
  }'
```

**Example Response:**

```json
{
  "id": "c4d5e6f7-a8b9-0123-cdef-123456789012",
  "email": "newuser@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "New User",
  "created_at": "2026-02-25T08:15:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | Email is already registered |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | Invalid email, password too short, or missing required fields (includes `details` array) |

---

### GET /users/{user_id}

Retrieve a specific user by their UUID. A non-superuser can only retrieve their own record.

**Authentication:** Required (Bearer token)
**Authorization:** Superuser, or the user requesting their own record

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | The target user's identifier |

**Response (200):**

Returns the target `UserPublic` object.

**Example Request:**

```bash
# Superuser fetching any user
curl -X GET "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <superuser_access_token>"
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
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Non-superuser requesting another user's record |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | No user exists with the given `user_id` (superuser only; non-superusers receive 403 first) |

> Note: The order of checks is: (1) if the requested user matches the caller, return immediately; (2) if the caller is not a superuser, raise 403; (3) if the user does not exist, raise 404.

---

### PATCH /users/{user_id}

Update any user's account fields. Superuser only.

**Authentication:** Required (Bearer token)
**Authorization:** Superuser only

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | The target user's identifier |

**Request Body (all fields optional):**

```json
{
  "email": "updated@example.com",
  "password": "newPass1234",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Updated Name"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string (email) \| null | No | max 255 chars, unique | New email address |
| `password` | string \| null | No | min 8, max 128 chars | New password (hashed before storage) |
| `is_active` | boolean | No | — | Toggle account active status |
| `is_superuser` | boolean | No | — | Toggle admin privileges |
| `full_name` | string \| null | No | max 255 chars | New display name |

**Response (200):**

Returns the updated `UserPublic` object.

**Example Request:**

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <superuser_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

**Example Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": false,
  "is_superuser": false,
  "full_name": "Jane Doe",
  "created_at": "2026-01-15T10:30:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | No user with the given `user_id` |
| `409 Conflict` | `CONFLICT` | `CONFLICT` | The requested email is already in use by a different account |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | Constraint violations on submitted fields (includes `details` array) |

---

### DELETE /users/{user_id}

Delete a user account and all their associated items. Superuser only. A superuser cannot delete their own account through this endpoint.

**Authentication:** Required (Bearer token)
**Authorization:** Superuser only

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | The target user's identifier |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | `"User deleted successfully"` |

> Note: Deleting a user also deletes all items owned by that user (cascade delete).

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <superuser_access_token>"
```

**Example Response:**

```json
{
  "message": "User deleted successfully"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Superuser attempting to delete their own account |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | No user with the given `user_id` |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.1.0 | 2026-02-27 | AYG-65: Auth updated to Clerk JWT; all error tables updated to unified error shape |
| 1.0.0 | 2026-02-26 | Initial release |
