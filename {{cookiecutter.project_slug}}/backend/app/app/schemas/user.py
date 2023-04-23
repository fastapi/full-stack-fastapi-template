from typing import Optional, Type, Any

from pydantic import BaseModel, EmailStr, validator

from app.models.role import Role


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role: Optional[Any] = None

    @validator("role")
    def validate_role(cls, val):
        print("Type is:", type(val))
        if issubclass(type(val), Role):
            return val

        raise TypeError("Wrong type for 'role', must be subclass of Role")

    class Config:
        arbitrary_types_allowed = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
