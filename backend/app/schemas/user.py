import uuid

from pydantic import EmailStr, Field
from sqlmodel import SQLModel


# Shared properties
class UserBase(SQLModel):
    """Base User schema with common attributes."""
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """Schema for user registration."""
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    """Schema for updating a user."""
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """Schema for updating own user information."""
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Schema for updating password."""
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    """Schema for public user information returned via API."""
    id: uuid.UUID


class UsersPublic(SQLModel):
    """Schema for returning a list of users."""
    data: list[UserPublic]
    count: int


class NewPassword(SQLModel):
    """Schema for setting a new password with a reset token."""
    token: str
    new_password: str = Field(min_length=8, max_length=40) 