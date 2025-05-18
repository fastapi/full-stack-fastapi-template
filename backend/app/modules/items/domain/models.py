"""
Item domain models.

This module contains domain models related to items.
"""
import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.shared.models import BaseModel

# Import User model from users module
from app.modules.users.domain.models import User


# Shared properties
class ItemBase(SQLModel):
    """Base item model with common properties."""

    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    """Model for creating an item."""
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    """Model for updating an item."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Item model definition
class Item(ItemBase, BaseModel, table=True):
    """Database model for an item."""

    __tablename__ = "item"

    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional[User] = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    """Public item model for API responses."""

    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """List of public items for API responses."""

    data: List[ItemPublic]
    count: int