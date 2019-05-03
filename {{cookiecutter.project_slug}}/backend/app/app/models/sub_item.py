from pydantic import BaseModel

from .item import Item


# Shared properties
class SubItemBase(BaseModel):
    name: str = None
    item_id: int


# Properties to receive on item creation
class SubItemCreate(SubItemBase):
    name: str


# Properties to receive on item update
class SubItemUpdate(SubItemBase):
    item_id: int = None


# Properties shared by models stored in DB
class SubItemInDBBase(SubItemBase):
    id: int
    name: str


# Properties to return to client
class SubItem(SubItemInDBBase):
    item : Item


# Properties properties stored in DB
class SubItemInDB(SubItemInDBBase):
    pass
