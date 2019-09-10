from pydantic import BaseModel

from .item import Item


# Shared properties
class SubItemBase(BaseModel):
    title: str = None
    description: str = None
    item_id: int = None

    class Config:
        orm_mode = True


# Mandatory properties for item creation
class SubItemCreate(SubItemBase):
    title: str
    item_id: int


# Specific properties to receive on item update
class SubItemUpdate(SubItemBase):
    pass


# Properties shared by models stored in DB
class SubItemInDBBase(SubItemBase):
    id: int


# Properties to return to client
class SubItem(SubItemInDBBase):
    item: Item
