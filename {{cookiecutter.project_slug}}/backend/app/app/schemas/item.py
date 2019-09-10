from typing import List, Optional
from pydantic import BaseModel

from .user import User

# Shared properties
class ItemBase(BaseModel):
    title: str = None
    description: str = None
    owner_id: int = None

    class Config:
        orm_mode = True


# Mandatory properties for item creation
class ItemCreate(ItemBase):
    title: str
    owner_id: int


# Specific properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int


# Properties to return to client
class Item(ItemInDBBase):
    owner: User


class ItemExpanded(ItemInDBBase):
    owner: User
    subitems: Optional[List['SubItem']]
