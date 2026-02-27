"""Shared Pydantic models for common API response shapes.

These are pure Pydantic models (not SQLModel ORM tables). They define
standard response envelopes reused across all API routes.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response shape for all API errors."""

    error: str
    """HTTP status category: BAD_REQUEST, NOT_FOUND, INTERNAL_SERVER_ERROR, etc."""

    message: str
    """Human-readable error description."""

    code: str
    """Machine-readable UPPER_SNAKE_CASE error code."""

    request_id: str
    """UUID of the originating request for correlation."""


class ValidationErrorDetail(BaseModel):
    """Single validation error detail for one field."""

    field: str
    """Field path using dot notation for nested fields (e.g. 'address.street')."""

    message: str
    """Human-readable validation message for this field."""

    type: str
    """Error type identifier (e.g. 'missing', 'string_type', 'value_error')."""


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with per-field details.

    Extends ErrorResponse with a list of field-level validation failures.
    Typically returned with HTTP 422.
    """

    details: list[ValidationErrorDetail]
    """List of individual field validation errors."""


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response envelope.

    Usage::

        PaginatedResponse[UserPublic](data=users, count=total)
    """

    data: list[T]
    """Page of items."""

    count: int
    """Total number of items across all pages."""
