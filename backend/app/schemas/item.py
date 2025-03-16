import uuid

from pydantic import BaseModel, Field


# Shared properties
class ItemBase(BaseModel):
    """Base Item schema with common attributes."""
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    """Schema for updating an item."""
    title: str | None = Field(default=None, min_length=1, max_length=255)


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    """Schema for public item information returned via API."""
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(BaseModel):
    """Schema for returning a list of items."""
    data: list[ItemPublic]
    count: int 