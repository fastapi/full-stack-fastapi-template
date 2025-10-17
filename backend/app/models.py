import uuid
from datetime import datetime, timezone
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# =====================================================
# ✅ Common Base Models
# =====================================================

class BaseModel(SQLModel):
    """Base for all database models."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)


class BasePublic(SQLModel):
    """Base for all response (public) models."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =====================================================
# ✅ USER MODELS
# =====================================================

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)

class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(BaseModel, UserBase, table=True):
    hashed_password: str
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)


class UserPublic(BasePublic, UserBase):
    pass


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# =====================================================
# ✅ ITEM MODELS
# =====================================================

class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class Item(BaseModel, ItemBase, table=True):
    owner_id: str = Field(foreign_key="user.id", nullable=False)
    owner: Optional["User"] = Relationship(back_populates="items")


class ItemPublic(BasePublic, ItemBase):
    owner_id: str


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# =====================================================
# ✅ ORGANIZATION MODELS
# =====================================================

class OrganizationBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, index=True, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class Organization(BaseModel, OrganizationBase, table=True):
    pass


class OrganizationPublic(BasePublic, OrganizationBase):
    pass


class OrganizationsPublic(SQLModel):
    data: list[OrganizationPublic]
    count: int


# =====================================================
# ✅ AUTH / TOKEN / MISC MODELS
# =====================================================

class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: Optional[str] = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
