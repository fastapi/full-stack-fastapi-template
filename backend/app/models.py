import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import EmailStr
from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


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
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    templates: list["Template"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    template_versions: list["TemplateVersion"] = Relationship(
        back_populates="creator", cascade_delete=True
    )
    generations: list["Generation"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


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
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
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


class TemplateCategory(str, Enum):
    cover_letter = "cover_letter"
    email = "email"
    proposal = "proposal"
    other = "other"


class TemplateLanguage(str, Enum):
    fr = "fr"
    en = "en"
    zh = "zh"
    other = "other"


class TemplateVariableType(str, Enum):
    text = "text"
    list = "list"


class TemplateVariableConfig(SQLModel):
    required: bool = False
    type: TemplateVariableType = TemplateVariableType.text
    description: str = ""
    example: Any | None = None
    default: Any | None = None


class TemplateBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    category: TemplateCategory = TemplateCategory.other
    language: TemplateLanguage = TemplateLanguage.en
    tags: list[str] = Field(default_factory=list)


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: TemplateCategory | None = None
    language: TemplateLanguage | None = None
    tags: list[str] | None = None
    is_archived: bool | None = None


class TemplateVersionBase(SQLModel):
    content: str = Field(min_length=1)
    variables_schema: dict[str, TemplateVariableConfig] = Field(default_factory=dict)


class TemplateVersionCreate(TemplateVersionBase):
    pass


class Template(TemplateBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    tags: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    is_archived: bool = False
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    owner: User | None = Relationship(back_populates="templates")
    versions: list["TemplateVersion"] = Relationship(
        back_populates="template", cascade_delete=True
    )
    generations: list["Generation"] = Relationship(
        back_populates="template", cascade_delete=True
    )


class TemplateVersion(TemplateVersionBase, table=True):
    __table_args__ = (UniqueConstraint("template_id", "version"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    template_id: uuid.UUID = Field(
        foreign_key="template.id", nullable=False, ondelete="CASCADE"
    )
    version: int = Field(default=1, ge=1)
    variables_schema: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    created_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    template: Template | None = Relationship(back_populates="versions")
    creator: User | None = Relationship(back_populates="template_versions")
    generations: list["Generation"] = Relationship(back_populates="template_version")


class TemplateVersionPublic(TemplateVersionBase):
    id: uuid.UUID
    template_id: uuid.UUID
    version: int
    created_at: datetime | None = None
    created_by: uuid.UUID


class TemplatePublic(TemplateBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_archived: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    versions_count: int = 0
    latest_version: TemplateVersionPublic | None = None


class TemplateListPublic(TemplateBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_archived: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    versions_count: int = 0
    latest_version_number: int | None = None


class TemplatesPublic(SQLModel):
    data: list[TemplateListPublic]
    count: int


class TemplateVersionsPublic(SQLModel):
    data: list[TemplateVersionPublic]
    count: int


class GenerationBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    input_text: str = Field(min_length=1)
    extracted_values: dict[str, Any] = Field(default_factory=dict)
    output_text: str = Field(min_length=1)


class GenerationCreate(GenerationBase):
    template_id: uuid.UUID
    template_version_id: uuid.UUID


class GenerationUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    extracted_values: dict[str, Any] | None = None
    output_text: str | None = Field(default=None, min_length=1)


class Generation(GenerationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    template_id: uuid.UUID = Field(
        foreign_key="template.id", nullable=False, ondelete="CASCADE"
    )
    template_version_id: uuid.UUID = Field(
        foreign_key="templateversion.id", nullable=False, ondelete="CASCADE"
    )
    extracted_values: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    owner: User | None = Relationship(back_populates="generations")
    template: Template | None = Relationship(back_populates="generations")
    template_version: TemplateVersion | None = Relationship(
        back_populates="generations"
    )


class GenerationPublic(GenerationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    template_id: uuid.UUID
    template_version_id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GenerationsPublic(SQLModel):
    data: list[GenerationPublic]
    count: int


class ExtractVariablesRequest(SQLModel):
    template_version_id: uuid.UUID
    input_text: str = Field(min_length=1)
    profile_context: dict[str, Any] = Field(default_factory=dict)


class ExtractVariablesResponse(SQLModel):
    values: dict[str, Any]
    missing_required: list[str]
    confidence: dict[str, float]
    notes: dict[str, str] = Field(default_factory=dict)


class RenderStyle(SQLModel):
    tone: str = "professional"
    length: str = "medium"


class RenderTemplateRequest(SQLModel):
    template_version_id: uuid.UUID
    values: dict[str, Any] = Field(default_factory=dict)
    style: RenderStyle = Field(default_factory=RenderStyle)


class RenderTemplateResponse(SQLModel):
    output_text: str


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
