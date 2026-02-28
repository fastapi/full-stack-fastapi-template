"""Entity Pydantic models.

Defines the data shapes for the Entity resource used across API request
validation, response serialisation, and service-layer contracts.

All models are pure Pydantic BaseModel (not SQLModel) because persistence
is handled via the Supabase REST client rather than an ORM.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EntityBase(BaseModel):
    """Shared fields for all entity representations."""

    title: str = Field(min_length=1, max_length=255)
    """Human-readable entity title. Required, 1–255 characters."""

    description: str | None = Field(default=None, max_length=1000)
    """Optional freeform description. Maximum 1000 characters."""


class EntityCreate(EntityBase):
    """Payload for creating a new entity.

    Inherits ``title`` (required) and ``description`` (optional) from
    :class:`EntityBase`.
    """


class EntityUpdate(BaseModel):
    """Payload for partially updating an existing entity.

    Does NOT inherit :class:`EntityBase` so that every field is optional,
    enabling true partial-update (PATCH) semantics.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    """Updated title. Must be 1–255 characters if provided."""

    description: str | None = Field(default=None, max_length=1000)
    """Updated description. Maximum 1000 characters if provided."""


class EntityPublic(EntityBase):
    """Full entity representation returned to API consumers."""

    id: UUID
    """Unique identifier assigned by the database."""

    owner_id: str
    """Clerk user ID of the entity owner."""

    created_at: datetime
    """UTC timestamp of entity creation."""

    updated_at: datetime
    """UTC timestamp of the most recent entity update."""


class EntitiesPublic(BaseModel):
    """Paginated collection of entities returned to API consumers."""

    data: list[EntityPublic]
    """Ordered list of entity records for the current page."""

    count: int
    """Total number of entities matching the query (for pagination)."""
