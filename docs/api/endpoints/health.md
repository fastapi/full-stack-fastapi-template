---
title: "Operational Endpoints API"
doc-type: reference
status: current
version: "1.0.0"
base-url: "/"
last-updated: 2026-02-28
updated-by: "api-docs-writer (AYG-68)"
related-code:
  - backend/app/api/routes/health.py
  - backend/app/main.py
  - backend/app/core/config.py
related-docs:
  - docs/api/overview.md
  - docs/architecture/overview.md
tags: [api, rest, health, operations, liveness, readiness, version]
---

# Operational Endpoints API

## Overview

The operational endpoints provide container-orchestrator-compatible probes and
build metadata for this service. They are mounted at the **application root**
(not under `/api/v1`) so that Kubernetes, AWS ECS, and similar platforms can
reach them without API-version routing logic.

**Base URL:** `/` (root — no `/api/v1` prefix)
**Authentication:** None — all three endpoints are fully public

> These endpoints do **not** appear in the `/api/v1/openapi.json` spec and are
> not shown in the Swagger UI at `/docs`. They are intentionally excluded to
> keep the versioned API spec clean.

## Quick Start

```bash
# Liveness probe
curl http://localhost:8000/healthz

# Readiness probe
curl http://localhost:8000/readyz

# Build metadata
curl http://localhost:8000/version
```

---

## Endpoints

### GET /healthz

Liveness probe. Returns `200 OK` immediately with no dependency checks. Use
this endpoint to tell the orchestrator that the process is alive and the event
loop is running. It never contacts Supabase or any other external service.

**Authentication:** None
**Authorization:** Public

**Parameters:** None

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"ok"` |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/healthz"
```

**Example Response:**

```json
{"status": "ok"}
```

**Error Responses:**

This endpoint has no application-level error responses. A non-`200` reply
indicates a process crash or network-level failure, not an API error.

---

### GET /readyz

Readiness probe. Verifies that the service can accept traffic by checking
connectivity to Supabase. Returns `200` when all checks pass; returns `503`
when any dependency is unreachable.

Container orchestrators use the `200`/`503` distinction to gate traffic:
a pod that is alive (`/healthz` = 200) but not ready (`/readyz` = 503) is
kept out of the load-balancer rotation until dependencies recover.

**Authentication:** None
**Authorization:** Public

**Parameters:** None

**Supabase check logic:**

The check issues a lightweight `HEAD` request against a probe table via the
Supabase PostgREST client. It considers the server **reachable** even if the
table does not exist (PostgREST returns an HTTP-level `APIError` in that case,
which still proves connectivity). Only a connection-level failure — or a
missing Supabase client on `app.state` — is treated as `"error"`.

**Response (200 — ready):**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"ready"` |
| `checks` | object | Per-dependency check results |
| `checks.supabase` | string | `"ok"` when Supabase is reachable |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/readyz"
```

**Example Response (200 — ready):**

```json
{
  "status": "ready",
  "checks": {
    "supabase": "ok"
  }
}
```

**Example Response (503 — not ready):**

```json
{
  "status": "not_ready",
  "checks": {
    "supabase": "error"
  }
}
```

**Error Responses:**

| Status | When |
|--------|------|
| `200 OK` | Supabase is reachable (or PostgREST returned a table-level error, which still proves connectivity) |
| `503 Service Unavailable` | Supabase connection failed, timed out, or `app.state.supabase` is not initialised |

> **Note:** Unlike most API errors, the `503` response from `/readyz` does NOT
> use the [standard error shape](../overview.md#standard-error-responses). It
> returns the plain `{"status": "not_ready", "checks": {...}}` body shown above,
> because this endpoint is designed for machine consumption by orchestrators, not
> API clients.

---

### GET /version

Returns build metadata injected at container image build time via environment
variables. API gateways use this endpoint for service registration and
canary-deployment tracking.

**Authentication:** None
**Authorization:** Public

**Parameters:** None

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| `service_name` | string | Service identifier (from `SERVICE_NAME` env var; default `"my-service"`) |
| `version` | string | Semantic version string (from `SERVICE_VERSION` env var; default `"0.1.0"`) |
| `commit` | string | Git commit SHA of the deployed image (from `GIT_COMMIT` env var; default `"unknown"`) |
| `build_time` | string | ISO 8601 timestamp of the image build (from `BUILD_TIME` env var; default `"unknown"`) |
| `environment` | string | Active deployment environment (from `ENVIRONMENT` env var; e.g. `"local"`, `"staging"`, `"production"`) |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/version"
```

**Example Response:**

```json
{
  "service_name": "my-service",
  "version": "1.2.0",
  "commit": "a3f1c2d",
  "build_time": "2026-02-28T08:00:00Z",
  "environment": "production"
}
```

**Example Response (unset build vars — local development):**

```json
{
  "service_name": "my-service",
  "version": "0.1.0",
  "commit": "unknown",
  "build_time": "unknown",
  "environment": "local"
}
```

**Error Responses:**

This endpoint has no application-level error responses. It reads from
in-process settings and cannot fail at the application layer.

---

## Kubernetes Probe Configuration

Typical Kubernetes deployment snippet using these endpoints:

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /readyz
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 15
  failureThreshold: 3
```

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-02-28 | AYG-68: Initial release — `/healthz`, `/readyz`, `/version` |
