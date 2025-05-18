"""
User domain models.

This module contains domain models related to users and user operations.
"""
import uuid
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.shared.models import BaseModel


# Shared properties
class UserBase(SQLModel):
    """Base user model with common properties."""
    
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Model for creating a user."""
    
    password: str = Field(min_length=8, max_length=40)


# Properties to receive via API on user registration
class UserRegister(SQLModel):
    """Model for user registration."""
    
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    """Model for updating a user."""
    
    email: Optional[EmailStr] = Field(default=None, max_length=255)  # type: ignore
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """Model for a user to update their own profile."""
    
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Model for updating a user's password."""
    
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, BaseModel, table=True):
    """Database model for a user."""
    
    __tablename__ = "user"
    
    hashed_password: str
    items: List["Item"] = Relationship(  # type: ignore
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    """Public user model for API responses."""
    
    id: uuid.UUID


class UsersPublic(SQLModel):
    """List of public users for API responses."""
    
    data: List[UserPublic]
    count: int