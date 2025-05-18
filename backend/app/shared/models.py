"""
Shared base models for the application.

This module contains SQLModel base classes used across multiple modules.
"""
import datetime
import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class TimestampedModel(SQLModel):
    """Base model with created_at and updated_at fields."""
    
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=False,
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, 
        nullable=True,
    )


class UUIDModel(SQLModel):
    """Base model with UUID primary key."""
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )


class BaseModel(UUIDModel, TimestampedModel):
    """Base model with UUID primary key and timestamps."""
    pass


class PaginatedResponse(SQLModel):
    """Base model for paginated responses."""
    
    count: int
    
    @classmethod
    def create(cls, items: list, count: int):
        """Create a paginated response with the given items and count."""
        return cls(data=items, count=count)