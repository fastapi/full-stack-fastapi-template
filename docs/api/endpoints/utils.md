---
title: "Utils API"
doc-type: reference
status: current
version: "1.0.0"
base-url: "/api/v1"
last-updated: 2026-02-26
updated-by: "initialise skill"
related-code:
  - backend/app/api/routes/utils.py
  - backend/app/api/deps.py
  - backend/app/models.py
related-docs:
  - docs/api/overview.md
  - docs/architecture/overview.md
tags: [api, rest, utils, health]
---

# Utils API

## Overview

The utils router provides operational and administrative utility endpoints: a public health-check probe for liveness monitoring and a superuser-only endpoint to send a test email. All paths are prefixed with `/api/v1/utils`.

**Base URL:** `/api/v1/utils`
**Authentication:** None for health check; Bearer token (JWT HS256) for test email
**Tag:** `utils`

## Quick Start

```bash
# Health check (no auth required)
curl -X GET "http://localhost:8000/api/v1/utils/health-check/"
```

---

## Endpoints

### GET /utils/health-check/

Liveness probe — returns `true` to confirm the API is up and accepting requests. Suitable for use with Docker health checks, load balancers, and uptime monitors.

**Authentication:** Not required
**Authorization:** None — public endpoint

**Response (200):**

Returns the JSON boolean `true` (not an object wrapper).

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/utils/health-check/"
```

**Example Response:**

```json
true
```

**Error Responses:**

| Status | Detail | When |
|--------|--------|------|
| `5xx` | Server error | API process is running but an unexpected error occurred (rare) |

> Note: A non-`200` response or a connection refused error indicates the service is unhealthy.

---

### POST /utils/test-email/

Send a test email to a specified address to verify email delivery configuration. Superuser only.

**Authentication:** Required (Bearer token)
**Authorization:** Superuser only

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email_to` | string (email) | Yes | Destination email address for the test message |

> Note: `email_to` is passed as a **query parameter**, not in the request body.

**Response (201):**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | `"Test email sent"` |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/utils/test-email/?email_to=admin@example.com" \
  -H "Authorization: Bearer <superuser_access_token>"
```

**Example Response:**

```json
{
  "message": "Test email sent"
}
```

**Error Responses:**

| Status | Detail | When |
|--------|--------|------|
| `403 Forbidden` | `"The user doesn't have enough privileges"` | Caller is not a superuser |
| `403 Forbidden` | `"Could not validate credentials"` | Token is invalid or missing |
| `422 Unprocessable Entity` | Pydantic validation error | `email_to` is missing or not a valid email address |

> Note: This endpoint returns `201 Created` (not `200 OK`). Ensure your HTTP client or test suite does not treat 201 as an error.

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-02-25 | Initial release |
