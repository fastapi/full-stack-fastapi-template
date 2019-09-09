from pydantic import BaseModel

from .item import Item


# Shared properties
class SubItemBase(BaseModel):
    title: str = None
    description: str = None
    item_id: int

    class Config:
        orm_mode = True


# Properties to receive on item creation
class SubItemCreate(SubItemBase):
    title: str


# Properties to receive on item update
class SubItemUpdate(SubItemBase):
    item_id: int = None


# Properties shared by models stored in DB
class SubItemInDBBase(SubItemBase):
    id: int


# Properties to return to client
class SubItem(SubItemInDBBase):
    item : Item
