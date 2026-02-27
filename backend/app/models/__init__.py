"""Shared Pydantic model re-exports for the models package.

Import from here to avoid deep import paths in consuming modules::

    from app.models import ErrorResponse, PaginatedResponse, Principal
"""

from app.models.auth import Principal
from app.models.common import (
    ErrorResponse,
    PaginatedResponse,
    ValidationErrorDetail,
    ValidationErrorResponse,
)

__all__ = [
    "ErrorResponse",
    "PaginatedResponse",
    "Principal",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
]
