---
title: "Entities API"
doc-type: reference
status: active
version: "0.1.0"
base-url: "/api/v1"
last-updated: 2026-02-28
updated-by: "api-docs-writer (AYG-70)"
related-code:
  - backend/app/models/entity.py
  - backend/app/services/entity_service.py
  - backend/app/api/deps.py
  - backend/app/core/errors.py
related-docs:
  - docs/api/overview.md
  - docs/architecture/overview.md
  - docs/data/models.md
tags: [api, rest, entities]
---

# Entities API

> **Active as of AYG-70.** The entity route handlers are registered and live under `/api/v1/entities`. All five CRUD operations are implemented and tested.

## Overview

The entities router will provide full CRUD operations for the `Entity` resource. An entity is a user-owned record with a required title and an optional description. Every operation is scoped to the authenticated caller — entities are isolated by `owner_id` (the Clerk user ID), so users can only read, modify, or delete their own records. All paths will be prefixed with `/api/v1/entities`.

**Base URL:** `/api/v1/entities`
**Authentication:** Clerk JWT Bearer token — required for all endpoints
**Tag:** `entities`

The service functions `create_entity`, `get_entity`, `list_entities`, `update_entity`, and `delete_entity` in `backend/app/services/entity_service.py` define the exact behaviour documented here. See [API Overview — Authentication](../overview.md#authentication) for the full Clerk auth flow. All error responses use the [unified error shape](../overview.md#standard-error-responses).

## Quick Start

```bash
# List your entities
curl -X GET "http://localhost:8000/api/v1/entities" \
  -H "Authorization: Bearer <clerk_jwt>"
```

---

## Endpoints

### POST /entities

Create a new entity. The caller automatically becomes the entity's owner via the `owner_id` field, which is set server-side from the verified Clerk principal and is never accepted from the request body.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user

**Request Body:**

```json
{
  "title": "My Entity",
  "description": "An optional description"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | Yes | min 1, max 255 chars | Human-readable entity title |
| `description` | string \| null | No | max 1000 chars | Optional freeform description |

**Response (201 Created):**

Returns the newly created `EntityPublic` object. `owner_id` is set to the Clerk user ID of the caller.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Newly assigned entity identifier |
| `title` | string | Entity title |
| `description` | string \| null | Optional description |
| `owner_id` | string | Clerk user ID of the entity owner |
| `created_at` | datetime | UTC creation timestamp |
| `updated_at` | datetime | UTC timestamp of the most recent update |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/entities" \
  -H "Authorization: Bearer <clerk_jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Entity",
    "description": "An optional description"
  }'
```

**Example Response:**

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
  "title": "My Entity",
  "description": "An optional description",
  "owner_id": "user_2abc123def456",
  "created_at": "2026-02-28T10:00:00+00:00",
  "updated_at": "2026-02-28T10:00:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `title` is missing, empty, or exceeds 255 chars; `description` exceeds 1000 chars (includes `details` array) |
| `500 Internal Server Error` | `INTERNAL_ERROR` | `ENTITY_CREATE_FAILED` | Supabase insert failed or returned no data |

---

### GET /entities/{entity_id}

Retrieve a single entity by its UUID. The service enforces `owner_id` isolation — the query filters by both `id` and `owner_id`, so a valid UUID belonging to a different user returns `404` rather than `403` to avoid leaking existence information.

**Authentication:** Required (Bearer token)
**Authorization:** Entity owner only

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity_id` | UUID | Yes | The entity's unique identifier |

**Response (200 OK):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Entity identifier |
| `title` | string | Entity title |
| `description` | string \| null | Optional description |
| `owner_id` | string | Clerk user ID of the entity owner |
| `created_at` | datetime | UTC creation timestamp |
| `updated_at` | datetime | UTC timestamp of the most recent update |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/entities/c3d4e5f6-a7b8-9012-cdef-345678901234" \
  -H "Authorization: Bearer <clerk_jwt>"
```

**Example Response:**

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
  "title": "My Entity",
  "description": "An optional description",
  "owner_id": "user_2abc123def456",
  "created_at": "2026-02-28T10:00:00+00:00",
  "updated_at": "2026-02-28T10:00:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `ENTITY_NOT_FOUND` | No entity with the given `entity_id` exists, or it is owned by a different user |
| `500 Internal Server Error` | `INTERNAL_ERROR` | `ENTITY_GET_FAILED` | Supabase query failed due to a network or database error |

---

### GET /entities

List entities owned by the authenticated caller. Results are paginated via `offset` and `limit`. Only the caller's own entities are returned — there is no superuser override for this resource.

**Authentication:** Required (Bearer token)
**Authorization:** Any active authenticated user (results scoped to caller)

**Query Parameters:**

| Parameter | Type | Required | Default | Max | Description |
|-----------|------|----------|---------|-----|-------------|
| `offset` | integer | No | `0` | — | Number of records to skip (must be ≥ 0) |
| `limit` | integer | No | `20` | `100` | Maximum records to return (capped at 100 by the service layer) |

**Response (200 OK):**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array[EntityPublic] | Ordered list of entity records for the current page |
| `count` | integer | Total number of entities owned by the caller (for pagination controls) |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/entities?offset=0&limit=20" \
  -H "Authorization: Bearer <clerk_jwt>"
```

**Example Response:**

```json
{
  "data": [
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
      "title": "My Entity",
      "description": "An optional description",
      "owner_id": "user_2abc123def456",
      "created_at": "2026-02-28T10:00:00+00:00",
      "updated_at": "2026-02-28T10:00:00+00:00"
    }
  ],
  "count": 1
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `offset` or `limit` are not valid integers (includes `details` array) |
| `500 Internal Server Error` | `INTERNAL_ERROR` | `ENTITY_LIST_FAILED` | Supabase query failed due to a network or database error |

---

### PATCH /entities/{entity_id}

Partially update an entity. Only fields included in the request body are written; omitted fields retain their current values. Sending an empty body `{}` is a no-op — the service returns the current entity without issuing a database write.

**Authentication:** Required (Bearer token)
**Authorization:** Entity owner only

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity_id` | UUID | Yes | The entity's unique identifier |

**Request Body:**

All fields are optional. At least one field should be provided for a meaningful update.

```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string \| null | No | min 1, max 255 chars | Updated title. Must be 1–255 characters if provided |
| `description` | string \| null | No | max 1000 chars | Updated description. Maximum 1000 characters if provided |

**Response (200 OK):**

Returns the updated (or unchanged) `EntityPublic` object.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Entity identifier |
| `title` | string | Entity title (updated or unchanged) |
| `description` | string \| null | Optional description (updated or unchanged) |
| `owner_id` | string | Clerk user ID of the entity owner |
| `created_at` | datetime | UTC creation timestamp (unchanged) |
| `updated_at` | datetime | UTC timestamp of the most recent update (refreshed on write) |

**Example Request:**

```bash
curl -X PATCH "http://localhost:8000/api/v1/entities/c3d4e5f6-a7b8-9012-cdef-345678901234" \
  -H "Authorization: Bearer <clerk_jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title"
  }'
```

**Example Response:**

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
  "title": "Updated Title",
  "description": "An optional description",
  "owner_id": "user_2abc123def456",
  "created_at": "2026-02-28T10:00:00+00:00",
  "updated_at": "2026-02-28T11:30:00+00:00"
}
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `ENTITY_NOT_FOUND` | No entity with the given `entity_id` exists, or it is owned by a different user |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | `VALIDATION_FAILED` | `title` is an empty string or fields exceed max length (includes `details` array) |
| `500 Internal Server Error` | `INTERNAL_ERROR` | `ENTITY_UPDATE_FAILED` | Supabase update query failed |

---

### DELETE /entities/{entity_id}

Delete an entity. The service enforces `owner_id` isolation — only the owning user can delete the record. Returns `204 No Content` on success with an empty body.

**Authentication:** Required (Bearer token)
**Authorization:** Entity owner only

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity_id` | UUID | Yes | The entity's unique identifier |

**Response (204 No Content):**

Empty body. The entity has been permanently deleted.

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/entities/c3d4e5f6-a7b8-9012-cdef-345678901234" \
  -H "Authorization: Bearer <clerk_jwt>"
```

**Example Response:**

```
HTTP/1.1 204 No Content
```

**Error Responses:**

All errors use the [standard error shape](../overview.md#standard-error-responses).

| Status | `error` | `code` | When |
|--------|---------|--------|------|
| `401 Unauthorized` | `UNAUTHORIZED` | `UNAUTHORIZED` | No `Authorization` header supplied |
| `403 Forbidden` | `FORBIDDEN` | `FORBIDDEN` | Clerk token is invalid, expired, or cannot be verified |
| `404 Not Found` | `NOT_FOUND` | `ENTITY_NOT_FOUND` | No entity with the given `entity_id` exists, or it is owned by a different user |
| `500 Internal Server Error` | `INTERNAL_ERROR` | `ENTITY_DELETE_FAILED` | Supabase delete query failed |

---

## Error Code Reference

All entity-specific error codes beyond the standard auth codes:

| `code` | HTTP Status | Description |
|--------|-------------|-------------|
| `ENTITY_NOT_FOUND` | `404` | Entity does not exist, or the caller does not own it |
| `ENTITY_CREATE_FAILED` | `500` | Supabase insert failed or returned no data |
| `ENTITY_GET_FAILED` | `500` | Supabase select query failed |
| `ENTITY_LIST_FAILED` | `500` | Supabase list query failed |
| `ENTITY_UPDATE_FAILED` | `500` | Supabase update query failed |
| `ENTITY_DELETE_FAILED` | `500` | Supabase delete query failed |

---

## Schema Reference

### EntityCreate

Request body for `POST /entities`.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `title` | string | Yes | min 1, max 255 chars |
| `description` | string \| null | No | max 1000 chars |

### EntityUpdate

Request body for `PATCH /entities/{entity_id}`. All fields are optional.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `title` | string \| null | No | min 1, max 255 chars if provided |
| `description` | string \| null | No | max 1000 chars if provided |

### EntityPublic

Returned by all endpoints that return a single entity.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier assigned by the database |
| `title` | string | Human-readable entity title (1–255 chars) |
| `description` | string \| null | Optional freeform description (max 1000 chars) |
| `owner_id` | string | Clerk user ID of the entity owner |
| `created_at` | datetime | UTC timestamp of entity creation |
| `updated_at` | datetime | UTC timestamp of the most recent entity update |

### EntitiesPublic

Returned by `GET /entities`.

| Field | Type | Description |
|-------|------|-------------|
| `data` | array[EntityPublic] | Ordered list of entity records for the current page |
| `count` | integer | Total number of entities owned by the caller |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-02-28 | AYG-69: Pre-scaffolded from service layer contract; routes planned for AYG-70 |
