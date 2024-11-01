"""
Base model class for all models in the application.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class BaseTimeModel(SQLModel, ABC):
    """
    Base class for models that require timestamp fields.

    Attributes:
        created_at (Optional[datetime]): The timestamp when the model instance was created.
        updated_at (Optional[datetime]): The timestamp when the model instance was last updated.
    """

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    @abstractmethod
    def to_read_schema(self):
        """Convert the model instance to its read schema representation."""

    @classmethod
    @abstractmethod
    def from_create_schema(cls, schema):
        """Create a model instance from the provided create schema."""
