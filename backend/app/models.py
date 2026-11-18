import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import EmailStr, computed_field, model_validator
from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


class UserRole(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    role: UserRole = Field(default=UserRole.MEMBER, sa_type=String(16))
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    is_superuser: bool | None = Field(default=None, exclude=True)

    @model_validator(mode="before")
    @classmethod
    def map_legacy_superuser(cls, values: object) -> object:
        if isinstance(values, dict) and values.get("is_superuser") is not None:
            values = values.copy()
            if "role" not in values:
                values["role"] = (
                    UserRole.ADMIN if values["is_superuser"] else UserRole.MEMBER
                )
        return values


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    role: UserRole | None = Field(default=None, sa_type=String(16))
    is_superuser: bool | None = Field(default=None, exclude=True)
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @model_validator(mode="before")
    @classmethod
    def map_legacy_superuser(cls, values: object) -> object:
        if isinstance(values, dict) and values.get("is_superuser") is not None:
            values = values.copy()
            if "role" not in values:
                values["role"] = (
                    UserRole.ADMIN if values["is_superuser"] else UserRole.MEMBER
                )
        return values


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)

    @property
    def is_superuser(self) -> bool:
        return self.role == UserRole.ADMIN


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    role: UserRole
    created_at: datetime | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_superuser(self) -> bool:
        return self.role == UserRole.ADMIN


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class MetricsPublic(SQLModel):
    user_count: int
    item_count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
