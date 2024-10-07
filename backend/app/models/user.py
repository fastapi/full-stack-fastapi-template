import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .item import Item


# Shared properties
class UserBase(SQLModel):
    """
    Base class for user properties.
    """

    # User's email address, must be unique and indexed
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    # Flag to indicate if the user account is active
    is_active: bool = True
    # Flag to indicate if the user has superuser privileges
    is_superuser: bool = False
    # User's full name, optional
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """
    Class for creating a new user.
    """

    # Password field with length constraints
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """
    Class for user registration.
    """

    # Email field for registration
    email: EmailStr = Field(max_length=255)
    # Password field with length constraints
    password: str = Field(min_length=8, max_length=40)
    # Optional full name field
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    """
    Class for updating user information.
    """

    # Optional email field for updates
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    # Optional password field for updates
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """
    Class for updating user information.
    """

    # Optional full name field for self-updates
    full_name: str | None = Field(default=None, max_length=255)
    # Optional email field for self-updates
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """
    Class for updating user password.
    """

    # Current password field
    current_password: str = Field(min_length=8, max_length=40)
    # New password field
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    """
    Database model for user.
    """

    # Unique identifier for the user
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Hashed password field
    hashed_password: str
    # Relationship to items model
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    """
    Public properties for user.
    """

    # Public user ID
    id: uuid.UUID


class UsersPublic(SQLModel):
    """
    Public properties for users.
    """

    # List of public user data
    data: list[UserPublic]
    # Total count of users
    count: int
