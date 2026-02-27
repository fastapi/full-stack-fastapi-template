"""Unified error handling framework.

Provides ServiceError exception, HTTP status code mapping, and global
exception handlers that format all API errors into a standard JSON shape.
"""

import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models.common import (
    ErrorResponse,
    ValidationErrorDetail,
    ValidationErrorResponse,
)

logger = logging.getLogger(__name__)

# HTTP status code → error category mapping
STATUS_CODE_MAP: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


class ServiceError(Exception):
    """Application-level error with structured error info.

    Usage::

        raise ServiceError(
            status_code=404,
            message="Entity not found",
            code="ENTITY_NOT_FOUND",
        )
    """

    def __init__(self, status_code: int, message: str, code: str) -> None:
        self.status_code = status_code
        self.message = message
        self.code = code
        self.error = STATUS_CODE_MAP.get(status_code, "INTERNAL_ERROR")
        super().__init__(message)


def _get_request_id(request: Request) -> str:
    """Extract request_id from request state, or generate a new UUID."""
    return getattr(request.state, "request_id", None) or str(uuid4())


async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    """Handle ServiceError exceptions."""
    request_id = _get_request_id(request)
    body = ErrorResponse(
        error=exc.error,
        message=exc.message,
        code=exc.code,
        request_id=request_id,
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI/Starlette HTTPException."""
    request_id = _get_request_id(request)
    error = STATUS_CODE_MAP.get(exc.status_code, "INTERNAL_ERROR")
    message = str(exc.detail) if exc.detail else error
    body = ErrorResponse(
        error=error,
        message=message,
        code=error,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic RequestValidationError with field-level details."""
    request_id = _get_request_id(request)
    details = []
    for err in exc.errors():
        # Convert loc tuple to dot-notation field path.
        # loc is like ("body", "title") or ("query", "page").
        # Skip the first element if it's a location prefix.
        loc_parts = [str(part) for part in err.get("loc", [])]
        if loc_parts and loc_parts[0] in ("body", "query", "path", "header", "cookie"):
            loc_parts = loc_parts[1:]
        field = ".".join(loc_parts) if loc_parts else "unknown"
        details.append(
            ValidationErrorDetail(
                field=field,
                message=err.get("msg", "Validation error"),
                type=err.get("type", "value_error"),
            )
        )
    body = ValidationErrorResponse(
        error="VALIDATION_ERROR",
        message="Request validation failed.",
        code="VALIDATION_FAILED",
        request_id=request_id,
        details=details,
    )
    return JSONResponse(status_code=422, content=body.model_dump())


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    request_id = _get_request_id(request)
    logger.exception("Unhandled exception [request_id=%s]", request_id, exc_info=exc)
    body = ErrorResponse(
        error="INTERNAL_ERROR",
        message="An unexpected error occurred.",
        code="INTERNAL_ERROR",
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=body.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""
    app.add_exception_handler(ServiceError, service_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
