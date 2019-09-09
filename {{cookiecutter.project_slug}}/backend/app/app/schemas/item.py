from pydantic import BaseModel

from .user import User

# Shared properties
class ItemBase(BaseModel):
    title: str = None
    description: str = None
    owner_id: int = None

    class Config:
        orm_mode = True


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str
    owner_id: int


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int
    title: str

    owner: User


# Properties to return to client
class Item(ItemInDBBase):
    pass
