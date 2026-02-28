---
title: "ADR-0001: Unified Error Handling Framework"
doc-type: reference
status: accepted
date: 2026-02-28
decision-makers: ["@amostan"]
last-updated: 2026-02-28
updated-by: "architecture-docs-writer"
related-code:
  - backend/app/core/errors.py
  - backend/app/models/common.py
  - backend/app/main.py
related-docs:
  - docs/architecture/overview.md
tags: [architecture, adr, error-handling]
---

# ADR-0001: Unified Error Handling Framework

## Context and Problem Statement

The existing codebase raises `HTTPException` directly from route handlers and dependencies, resulting in inconsistent error response shapes across the API. Some routes return `{"detail": "..."}`, others return structured objects, and unhandled exceptions produce default Starlette HTML error pages. Consumers of the API (frontend, mobile clients, third-party integrations) cannot rely on a single error contract, making client-side error handling fragile and difficult to maintain.

## Decision Drivers

- API consumers need a predictable, machine-parseable error format for all failure modes
- Error correlation across distributed systems requires a `request_id` field in every error response
- Validation errors need field-level detail (not just a single message) for form-driven UIs
- Unhandled exceptions must never leak stack traces or implementation details to clients

## Considered Options

1. **Centralized exception handlers with `ServiceError` exception** - Register global handlers on the FastAPI app that intercept `ServiceError`, `HTTPException`, `RequestValidationError`, and `Exception`, formatting all into a standard JSON envelope
2. **Middleware-based error wrapping** - Use a Starlette middleware that catches all exceptions and reformats responses
3. **Per-route try/except with helper functions** - Provide utility functions that each route handler calls in its own try/except block

<!-- OPTIONAL -->
### Option 1: Centralized exception handlers with ServiceError

**Pros:**
- Single registration point (`register_exception_handlers(app)`) keeps `main.py` clean
- `ServiceError` provides structured fields (`status_code`, `message`, `code`, `error`) for application-level errors
- `STATUS_CODE_MAP` ensures consistent error category naming across all HTTP status codes
- Validation handler produces per-field error details compatible with form UIs
- Catch-all handler prevents stack trace leakage while logging the full exception

**Cons:**
- Global handlers can mask bugs if the catch-all silently swallows important exceptions (mitigated by `logger.exception` call)
- Developers must learn to raise `ServiceError` instead of `HTTPException` for new application errors

### Option 2: Middleware-based error wrapping

**Pros:**
- Catches errors at the ASGI layer, covering even middleware-level failures
- Single point of control

**Cons:**
- Middleware runs outside FastAPI's exception handling pipeline, losing access to `RequestValidationError` details
- Response body must be reconstructed from raw bytes, complicating structured error formatting
- Harder to unit test in isolation

### Option 3: Per-route try/except with helper functions

**Pros:**
- Explicit error handling at each route, visible in code review
- No global state

**Cons:**
- Boilerplate duplication across every route handler
- Easy to forget in new routes, leading to inconsistent error shapes
- Cannot intercept framework-level exceptions (validation errors, 404s for missing routes)
<!-- /OPTIONAL -->

## Decision Outcome

**Chosen option:** "Centralized exception handlers with ServiceError"

**Reason:** This approach provides a single registration point that guarantees every API response -- whether from application logic, framework validation, or unexpected failures -- conforms to the standard `{error, message, code, request_id}` JSON shape. The `ServiceError` exception gives application code a clean, typed way to signal errors with explicit status codes and machine-readable codes, while the catch-all handler ensures no unformatted exceptions reach clients.

### Positive Consequences

- All API errors now return a consistent JSON envelope: `{error: str, message: str, code: str, request_id: str}`
- Validation errors (HTTP 422) include field-level `details` array with `{field, message, type}` objects
- Every error response carries a `request_id` for log correlation and debugging
- Unhandled exceptions are logged with full traceback but return only a generic message to clients
- New application errors are raised as `ServiceError(status_code, message, code)` with no boilerplate

### Negative Consequences

- Existing code that catches `HTTPException` at the route level and reformats it will need to be reviewed to avoid double-handling (mitigated by the global handler taking precedence)
- Team must adopt the convention of raising `ServiceError` for application errors; `HTTPException` still works but produces less specific error codes (mitigated by documentation and code review)
