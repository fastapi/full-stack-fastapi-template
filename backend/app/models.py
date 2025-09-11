"""Data models for the application."""

import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

# Token type constant to avoid hardcoded string
TOKEN_TYPE_BEARER = "bearer"  # noqa: S105


# Shared properties
class UserBase(SQLModel):
    """Base user model with shared fields."""

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """User registration model."""

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    """User update model."""

    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """User self-update model."""

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Password update model."""

    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    """Database user model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    """Public user model for API responses."""

    id: uuid.UUID


class UsersPublic(SQLModel):
    """Collection of public users."""

    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    """Base item model with shared fields."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    """Item creation model."""



# Properties to receive on item update
class ItemUpdate(ItemBase):
    """Item update model."""

    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore[assignment]


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    """Database item model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    """Public item model for API responses."""

    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """Collection of public items."""

    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    """Generic message model."""

    message: str


# JSON payload containing access token
class Token(SQLModel):
    """JWT token model."""

    access_token: str
    token_type: str = TOKEN_TYPE_BEARER


# Contents of JWT token
class TokenPayload(SQLModel):
    """JWT token payload model."""

    sub: str | None = None


class NewPassword(SQLModel):
    """New password model."""

    token: str
    new_password: str = Field(min_length=8, max_length=40)
