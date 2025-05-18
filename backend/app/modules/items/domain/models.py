"""
Item domain models.

This module contains domain models related to items.
"""
import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.shared.models import BaseModel

# Use legacy Item model from app.models to avoid conflict
# This is a transitional measure until the legacy model can be fully removed
from app.models import Item, User


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


# Do not define a duplicate Item model
# Remove this after all references to models.Item are removed
# class Item(ItemBase, BaseModel, table=True):
#     """Database model for an item."""
#     
#     __tablename__ = "item"
#     
#     owner_id: uuid.UUID = Field(
#         foreign_key="user.id", nullable=False, ondelete="CASCADE"
#     )
#     owner: Optional[User] = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    """Public item model for API responses."""
    
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """List of public items for API responses."""
    
    data: List[ItemPublic]
    count: int