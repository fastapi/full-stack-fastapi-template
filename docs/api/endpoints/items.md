---
title: "Items API"
doc-type: reference
status: current
version: "1.1.0"
base-url: "/api/v1"
last-updated: 2026-02-27
updated-by: "api-docs-writer (AYG-65)"
related-code:
  - backend/app/api/routes/items.py
  - backend/app/api/deps.py
  - backend/app/core/errors.py
  - backend/app/models.py
related-docs:
  - docs/api/overview.md
  - docs/architecture/overview.md
  - docs/data/models.md
tags: [api, rest, items]
---

# Items API

## Overview

The items router provides CRUD operations for the `Item` resource. Each item belongs to an owner (the user who created it). Regular users can only read, update, and delete their own items; superusers can access all items regardless of ownership. All paths are prefixed with `/api/v1/items`.

**Base URL:** `/api/v1/items`
**Authentication:** Clerk JWT Bearer token — required for all endpoints
**Tag:** `items`

> **AYG-65:** Auth dependency updated from internal HS256 JWT to Clerk JWT. The client must supply a Clerk-issued token as `Authorization: Bearer <clerk_jwt>`. See [API Overview — Authentication](../overview.md#authentication) for the full flow. All error responses now use the [unified error shape](../overview.md#standard-error-responses).

## Quick Start

```bash
# List your items
curl -X GET "http://localhost:8000/api/v1/items/" \
  -H "Authorization: Bearer <access_token>"
```

---

## Endpoints

### GET /items/

List items. Superusers see all items; regular users see only their own. Results are ordered by `created_at` descending.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | integer | No | `0` | Number of records to skip |
| `limit` | integer | No | `100` | Maximum records to return |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array[ItemPublic] | List of items, ordered by `created_at` descending |
| `count` | integer | Total number of matching items (respects ownership filter) |

**Example Request (regular user):**

```bash
curl -X GET "http://localhost:8000/api/v1/items/?skip=0&limit=20" \
  -H "Authorization: Bearer <access_token>"
```

**Example Response:**

```json
{
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "My First Item",
      "description": "A short description",
      "owner_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-02-20T14:00:00+00:00"
    }
  ],
  "count": 1
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `400 Bad Request` | `BAD_REQUEST` | `BAD_REQUEST` | Account has been deactivated |
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `skip` or `limit` are not valid integers (includes `details` array) |

---

### GET /items/{id}

Retrieve a single item by its UUID. Regular users may only access items they own.

**Authentication:** Required (Bearer token)
**Authorization:** Item owner or superuser

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | The item's unique identifier |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Item identifier |
| `title` | string | Item title |
| `description` | string \| null | Optional description |
| `owner_id` | UUID | UUID of the owning user |
| `created_at` | datetime \| null | UTC creation timestamp |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/items/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "Authorization: Bearer <access_token>"
```

**Example Response:**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "My First Item",
  "description": "A short description",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-20T14:00:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not the item owner and not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | No item exists with the given `id` |

---

### POST /items/

Create a new item. The caller automatically becomes the item's owner.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user

**Request Body:**

```json
{
  "title": "My New Item",
  "description": "An optional description"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | Yes | min 1, max 255 chars | Item title |
| `description` | string \| null | No | max 255 chars | Optional item description |

**Response (200):**

Returns the created `ItemPublic` object. The `owner_id` is automatically set to the caller's user ID.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Newly assigned item identifier |
| `title` | string | Item title |
| `description` | string \| null | Optional description |
| `owner_id` | UUID | UUID of the creating user |
| `created_at` | datetime \| null | UTC creation timestamp |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Item",
    "description": "An optional description"
  }'
```

**Example Response:**

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
  "title": "My New Item",
  "description": "An optional description",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-25T08:30:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `title` is missing, empty, or exceeds 255 characters; `description` exceeds 255 characters (includes `details` array) |

---

### PUT /items/{id}

Fully replace an item's fields. Regular users may only update items they own.

**Authentication:** Required (Bearer token)
**Authorization:** Item owner or superuser

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | The item's unique identifier |

**Request Body:**

```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string \| null | No | min 1, max 255 chars | New title (omit to keep existing) |
| `description` | string \| null | No | max 255 chars | New description (omit to keep existing) |

> Note: Although this is a `PUT` endpoint, only fields included in the request body are updated (`exclude_unset=True`). Omitted fields retain their current values.

**Response (200):**

Returns the updated `ItemPublic` object.

**Example Request:**

```bash
curl -X PUT "http://localhost:8000/api/v1/items/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "description": "Updated description"
  }'
```

**Example Response:**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Updated Title",
  "description": "Updated description",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-20T14:00:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not the item owner and not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | No item exists with the given `id` |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `title` is empty string or fields exceed max length (includes `details` array) |

---

### DELETE /items/{id}

Delete an item. Regular users may only delete items they own.

**Authentication:** Required (Bearer token)
**Authorization:** Item owner or superuser

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | The item's unique identifier |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | `"Item deleted successfully"` |

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/items/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "Authorization: Bearer <access_token>"
```

**Example Response:**

```json
{
  "message": "Item deleted successfully"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Caller is not the item owner and not a superuser |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `NOT_FOUND` | No item exists with the given `id` |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.1.0 | 2026-02-27 | AYG-65: Auth updated to Clerk JWT; all error tables updated to unified error shape |
| 1.0.0 | 2026-02-26 | Initial release |
