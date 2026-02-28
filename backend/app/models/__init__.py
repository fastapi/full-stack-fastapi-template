"""Shared Pydantic model re-exports for the models package.

Import from here to avoid deep import paths in consuming modules::

    from app.models import ErrorResponse, PaginatedResponse, Principal
    from app.models import EntityCreate, EntityPublic, EntitiesPublic
"""

from app.models.auth import Principal
from app.models.common import (
    ErrorResponse,
    PaginatedResponse,
    ValidationErrorDetail,
    ValidationErrorResponse,
)
from app.models.entity import (
    EntitiesPublic,
    EntityCreate,
    EntityPublic,
    EntityUpdate,
)

__all__ = [
    "EntitiesPublic",
    "EntityCreate",
    "EntityPublic",
    "EntityUpdate",
    "ErrorResponse",
    "PaginatedResponse",
    "Principal",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
]
