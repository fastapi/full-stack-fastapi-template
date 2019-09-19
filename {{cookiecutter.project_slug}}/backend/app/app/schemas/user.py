from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Schema


# Shared properties
class UserBase(BaseModel):
    email:str = None
    full_name:str = None
    is_active:bool = True
    is_superuser:bool = False

    class Config:
        orm_mode = True


# Additional properties stored in DB
class UserBaseInDB(UserBase):
    id: int = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Properties to receive via API on creation
class UserCreate(UserBaseInDB):
    email: str
    password: str
    created_at: datetime = Schema(datetime.utcnow())


# Properties to receive via API on update
class UserUpdate(UserBaseInDB):
    password: str = None
    updated_at: datetime = Schema(datetime.utcnow())


# Additional properties stored in DB
class UserInDB(UserBaseInDB):
    hashed_password: str


# Additional properties to return via API
class User(UserBaseInDB):
    pass


class UserExpanded(User):
    items: Optional[List['Item']]
