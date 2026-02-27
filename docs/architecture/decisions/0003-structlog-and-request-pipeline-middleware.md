---
title: "ADR-0003: Structlog Adoption and Request Pipeline Middleware"
doc-type: reference
status: accepted
date: 2026-02-27
decision-makers: ["Engineering team"]
last-updated: 2026-02-27
updated-by: "architecture-docs-writer"
related-code:
  - backend/app/core/logging.py
  - backend/app/core/middleware.py
  - backend/app/main.py
related-docs:
  - docs/architecture/overview.md
tags: [architecture, adr, logging, middleware, observability]
story: AYG-66
---

# ADR-0003: Structlog Adoption and Request Pipeline Middleware

## Context and Problem Statement

Prior to AYG-66, the template had no structured logging, no request tracing, and no security headers. Request IDs in error responses were placeholder strings not traceable to real requests. The application needed a logging solution that could produce structured JSON output for production observability tooling while remaining developer-friendly in local development, and a middleware layer to generate request IDs, propagate correlation IDs, and apply security headers uniformly across all response paths.

## Decision Drivers

- Structured JSON output required for production observability tooling (log aggregators, dashboards)
- `request_id` must propagate automatically from middleware through error handlers to error response body without explicit passing (contextvars)
- Security headers must appear on all responses including CORS preflight OPTIONS responses
- Single outermost middleware reduces coupling vs multiple specialized middlewares
- Local development needs human-readable console output, not JSON

## Considered Options

1. **stdlib logging with manual `json.dumps`** -- Use Python's built-in logging module with a custom JSON formatter
2. **loguru with custom JSON sink** -- Use loguru's structured logging with a custom sink for JSON output
3. **structlog with contextvars** -- Use structlog's processor pipeline with first-class contextvars support

<!-- OPTIONAL -->
### Option 1: stdlib logging with manual json.dumps

**Pros:**
- Zero additional dependencies
- Familiar to all Python developers

**Cons:**
- Verbose boilerplate for JSON formatting
- No built-in contextvars integration; request-scoped fields must be passed explicitly or managed manually
- Processor pipeline must be hand-rolled

### Option 2: loguru with custom JSON sink

**Pros:**
- Good developer experience with colorized output
- Simple API for common logging tasks

**Cons:**
- Less ecosystem integration with structlog-compatible processors
- Custom sink required for JSON output format
- contextvars support requires additional wrapper code
- Smaller ecosystem of reusable processors compared to structlog

### Option 3: structlog with contextvars

**Pros:**
- First-class contextvars support via `bind_contextvars` / `merge_contextvars`
- Composable processor pipeline (timestamping, log level, service info, rendering)
- Built-in `JSONRenderer` and `ConsoleRenderer` switchable by configuration
- Excellent FastAPI/Starlette integration patterns
- Wide adoption in Python observability ecosystem

**Cons:**
- Additional dependency (structlog >=24.1.0)
- Processor chain ordering must be understood and maintained
- `cache_logger_on_first_use=True` means configuration must be finalized before first log call
<!-- /OPTIONAL -->

## Decision Outcome

**Chosen option:** "structlog with contextvars"

**Reason:** structlog provides first-class contextvars support that enables automatic propagation of `request_id` and `correlation_id` from middleware into all log entries without explicit parameter passing. Its processor pipeline architecture cleanly separates concerns (timestamping, service metadata injection, rendering), and the built-in JSONRenderer/ConsoleRenderer switch eliminates custom formatting code. Combined with a single `RequestPipelineMiddleware` that handles request tracing, security headers, and structured request logging, this approach delivers observability, security, and developer ergonomics with minimal coupling.

### Positive Consequences

- `request_id` and `correlation_id` automatically present in all log lines without explicit parameter passing
- JSON/console rendering controlled by single `LOG_FORMAT` env var
- Security headers guaranteed on all response paths including CORS preflight OPTIONS responses
- Single middleware reduces the surface area for middleware ordering bugs compared to multiple specialized middlewares
- Request IDs in error responses (`ErrorResponse.request_id`) are now traceable to real request log entries

### Negative Consequences

- structlog contextvars must be cleared after each request to prevent leakage across requests (implemented in middleware as step 10 of the request lifecycle)
- Middleware ordering is a deployment constraint: `RequestPipelineMiddleware` must remain the outermost middleware (documented in Known Constraints in architecture overview)
- `cache_logger_on_first_use=True` means structlog config must be finalized before the first log call; module-level `setup_logging(settings)` in `main.py` satisfies this constraint

<!-- OPTIONAL -->
## More Information

- Related code: `backend/app/core/logging.py`, `backend/app/core/middleware.py`, `backend/app/main.py`
- Related docs: `docs/architecture/overview.md` (Request Pipeline section)
- Linear story: AYG-66
<!-- /OPTIONAL -->
