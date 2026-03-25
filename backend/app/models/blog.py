"""Pydantic schemas for blog endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BlogPostListItem(BaseModel):
    """Summary item used in the public list endpoint (no content field)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    excerpt: str
    category: str
    read_time_minutes: int
    author_name: str
    published_at: datetime


class BlogPostPublicResponse(BaseModel):
    """Full post for the public single-post endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    excerpt: str
    content: str
    category: str
    read_time_minutes: int
    author_name: str
    published_at: datetime


class BlogPostAdminResponse(BaseModel):
    """Full post with admin fields for admin endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    excerpt: str
    content: str
    category: str
    read_time_minutes: int
    author_name: str
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class BlogPostCreateRequest(BaseModel):
    slug: str
    title: str
    excerpt: str
    content: str
    category: str
    read_time_minutes: int
    author_name: str = "Kila Team"


class BlogPostUpdateRequest(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    read_time_minutes: Optional[int] = None
    author_name: Optional[str] = None
