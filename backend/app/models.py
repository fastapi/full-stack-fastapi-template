import uuid
from datetime import date as DateType, datetime
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


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
    organization_id: Optional[uuid.UUID] = Field(default=None, foreign_key="organization.id")
    organization: Optional["Organization"] = Relationship(back_populates="users")


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


# ============================================================================
# ORGANIZATION MODELS
# ============================================================================

class OrganizationBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    users: list["User"] = Relationship(back_populates="organization")
    projects: list["Project"] = Relationship(back_populates="organization", cascade_delete=True)


class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    created_at: datetime


class OrganizationsPublic(SQLModel):
    data: list[OrganizationPublic]
    count: int


# ============================================================================
# PROJECT MODELS
# ============================================================================

class ProjectBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    client_name: str = Field(min_length=1, max_length=255)
    client_email: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="planning", max_length=50)  # planning, in_progress, review, completed
    deadline: Optional[DateType] = None
    start_date: Optional[DateType] = None
    budget: Optional[str] = Field(default=None, max_length=100)
    progress: int = Field(default=0, ge=0, le=100)


class ProjectCreate(ProjectBase):
    organization_id: uuid.UUID


class ProjectUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    client_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    client_email: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None, max_length=50)
    deadline: Optional[DateType] = None
    start_date: Optional[DateType] = None
    budget: Optional[str] = Field(default=None, max_length=100)
    progress: Optional[int] = Field(default=None, ge=0, le=100)


class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", nullable=False, ondelete="CASCADE")
    organization: Optional["Organization"] = Relationship(back_populates="projects")
    galleries: list["Gallery"] = Relationship(back_populates="project", cascade_delete=True)


class ProjectPublic(ProjectBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    organization_id: uuid.UUID


class ProjectsPublic(SQLModel):
    data: list[ProjectPublic]
    count: int


# ============================================================================
# GALLERY MODELS
# ============================================================================

class GalleryBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    date: Optional[DateType] = None
    photo_count: int = Field(default=0, ge=0)
    photographer: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="draft", max_length=50)  # draft, processing, published
    cover_image_url: Optional[str] = Field(default=None, max_length=500)


class GalleryCreate(GalleryBase):
    project_id: uuid.UUID


class GalleryUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    date: Optional[DateType] = None
    photo_count: Optional[int] = Field(default=None, ge=0)
    photographer: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = Field(default=None, max_length=50)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)


class Gallery(GalleryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    project: Optional["Project"] = Relationship(back_populates="galleries")


class GalleryPublic(GalleryBase):
    id: uuid.UUID
    created_at: datetime
    project_id: uuid.UUID


class GalleriesPublic(SQLModel):
    data: list[GalleryPublic]
    count: int


# ============================================================================
# DASHBOARD STATS
# ============================================================================

class DashboardStats(SQLModel):
    active_projects: int
    upcoming_deadlines: int
    team_members: int
    completed_this_month: int
