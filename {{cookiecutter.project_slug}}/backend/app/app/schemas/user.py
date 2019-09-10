from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class UserBase(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: str
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


# Properties shared by models stored in DB
class UserBaseInDBBase(UserBase):
    id: int = None
    hashed_password: str


# Properties to return to client
class User(UserBaseInDBBase):
    pass


class UserExpanded(UserBaseInDBBase):
    items: Optional[List['Item']]
