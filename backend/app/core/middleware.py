"""Request pipeline middleware: request ID, correlation, security headers, logging.

Generates a UUID v4 request_id for every request, propagates correlation IDs,
applies security headers, and logs each request with status-appropriate level.

This middleware MUST be the outermost middleware (added last in code) so that
security headers and X-Request-ID are set on ALL responses, including CORS
preflight OPTIONS responses handled by CORSMiddleware.
"""

from __future__ import annotations

import re
import time
from typing import Any
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

# Correlation ID validation: alphanumeric, hyphens, underscores, dots; max 128 chars.
# Rejects injection payloads (newlines, control chars) that could forge log entries.
_CORRELATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_.]{1,128}$")

# Security headers applied to every response (PRD Section 4.1.12)
_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "0",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

# HSTS header only applied in production
_HSTS_VALUE = "max-age=31536000; includeSubDomains"


class RequestPipelineMiddleware(BaseHTTPMiddleware):
    """Middleware that provides request tracing, security headers, and request logging.

    Args:
        app: The ASGI application.
        environment: Deployment environment (e.g. "local", "staging", "production").
                     Controls whether HSTS header is applied.
    """

    def __init__(self, app: ASGIApp, environment: str = "local") -> None:
        super().__init__(app)
        self.environment = environment

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 1. Generate request_id (UUID v4)
        request_id = str(uuid4())

        # 2. Read X-Correlation-ID or fall back to request_id.
        #    Validate format to prevent log injection (SEC-001).
        raw_correlation = request.headers.get("x-correlation-id")
        if raw_correlation and _CORRELATION_ID_PATTERN.match(raw_correlation):
            correlation_id = raw_correlation
        else:
            correlation_id = request_id

        # 3. Store in request.state for downstream handlers and error handlers
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        # 4. Bind to structlog contextvars for automatic inclusion in all logs
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            correlation_id=correlation_id,
        )

        # 5. Record start time
        start = time.perf_counter()

        # 6. Process request — wrap in try/except so headers are set even
        #    when an exception propagates past all exception handlers.
        try:
            response = await call_next(request)
        except Exception:
            # Log the exception so it's not silently swallowed (BUG-001).
            # In practice, global exception handlers (errors.py) catch most
            # exceptions before they reach here.
            structlog.get_logger().exception(
                "unhandled_exception_in_middleware",
                method=request.method,
                path=request.url.path,
            )
            response = Response(
                content='{"error":"INTERNAL_ERROR","message":"An unexpected error occurred."}',
                status_code=500,
                media_type="application/json",
            )

        # 7. Calculate duration
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        # 8. Apply security headers
        _apply_security_headers(response, self.environment)

        # 9. Set X-Request-ID response header
        response.headers["X-Request-ID"] = request_id

        # 10. Log request with appropriate level based on status code
        _log_request(request, response, duration_ms)

        # 11. Clear contextvars after logging to prevent leakage (FUNC-001)
        structlog.contextvars.clear_contextvars()

        return response


def _apply_security_headers(response: Response, environment: str) -> None:
    """Apply security headers to the response."""
    for header, value in _SECURITY_HEADERS.items():
        response.headers[header] = value

    if environment == "production":
        response.headers["Strict-Transport-Security"] = _HSTS_VALUE


def _log_request(request: Request, response: Response, duration_ms: float) -> None:
    """Log the completed request at the appropriate level.

    - 2xx → info
    - 4xx → warning
    - 5xx → error
    """
    logger: Any = structlog.get_logger()

    log_kwargs: dict[str, Any] = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }

    # Include user_id if set by auth middleware/handler
    user_id = getattr(request.state, "user_id", None)
    if user_id is not None:
        log_kwargs["user_id"] = user_id

    status = response.status_code
    if status >= 500:
        logger.error("request_completed", **log_kwargs)
    elif status >= 400:
        logger.warning("request_completed", **log_kwargs)
    else:
        logger.info("request_completed", **log_kwargs)
