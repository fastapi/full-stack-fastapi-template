import uuid

from pydantic import EmailStr, HttpUrl
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


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
    new_password: str = Field(min_length=8, max_length=40)

# TreadEd specific models
## Database models
def utc_now():
    return datetime.now(timezone.utc)

class Path(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(max_length=255)
    path_summary: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    steps: list["Step"] = Relationship(back_populates="path", cascade_delete=True)

class YoutubeExposition(SQLModel):
    url: HttpUrl
    start_time: int | None = Field(default=None, ge=0)
    end_time: int | None = Field(default=None, ge=0)

# Base model with shared fields
class StepBase(SQLModel):
    number: int = Field(ge=0)
    role_prompt: str | None = Field(default=None)
    validation_prompt: str | None = Field(default=None)

# Database model, database table inferred from class name
class Step(StepBase, table=True):
    id: int = Field(default=None, primary_key=True)
    path_id: uuid.UUID = Field(foreign_key="path.id", nullable=False)
    exposition_json: str | None = Field(default=None)
    path: Path = Relationship(back_populates="steps")

# API Models
class StepCreate(StepBase):
    exposition: YoutubeExposition | None = None

class StepUpdate(StepBase):
    role_prompt: str | None = None
    validation_prompt: str | None = None
    exposition: YoutubeExposition | None = None

class StepPublic(StepBase):
    id: int
    exposition: YoutubeExposition | None = None

class StepInList(SQLModel):
    id: int
    number: int
    exposition: YoutubeExposition | None = None  # Include only what's needed for list view

class PathCreate(SQLModel):
    title: str
    path_summary: str | None = None
    steps: list[StepCreate]  # Make steps required for path creation

class PathUpdate(SQLModel):
    title: str | None = None
    path_summary: str | None = None

class PathPublic(SQLModel):
    id: uuid.UUID
    title: str
    path_summary: str | None
    steps: list[StepPublic]  # Always include steps with path

class PathInList(SQLModel):
    id: uuid.UUID
    title: str
    path_summary: str | None
    created_at: datetime

class PathsPublic(SQLModel):
    data: list[PathInList]
    count: int