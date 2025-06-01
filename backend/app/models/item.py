"""Item model for the application."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlmodel import SQLModel, Field as SQLModelField

from app.models.base import BaseDBModel


class ItemBase(SQLModel):
    """Base model for Item with common attributes."""
    title: str = SQLModelField(..., max_length=100, description="The title of the item")
    description: Optional[str] = SQLModelField(
        None, max_length=500, description="A description of the item"
    )
    price: float = SQLModelField(..., gt=0, description="The price of the item in USD")
    tax: Optional[float] = SQLModelField(None, ge=0, description="Tax applied to the item")


class ItemCreate(ItemBase):
    """Model for creating a new item."""
    pass


class ItemUpdate(SQLModel):
    """Model for updating an existing item."""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None


class Item(ItemBase, BaseDBModel, table=True):
    """Database model for items."""
    __tablename__ = "item"
    
    owner_id: UUID = SQLModelField(
        ..., foreign_key="user.id", description="ID of the user who owns this item"
    )


class ItemPublic(ItemBase):
    """Public representation of an item."""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class ItemsPublic(SQLModel):
    """Response model for a list of items."""
    data: list[ItemPublic]
    count: int


class Message(SQLModel):
    """Generic message response model."""
    message: str
