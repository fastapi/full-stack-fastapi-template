"""Blog endpoints: public read + super-user-only admin CRUD."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from kila_models.models.database import BlogPostTable, UsersTable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_super_user
from app.models.blog import (
    BlogPostAdminResponse,
    BlogPostCreateRequest,
    BlogPostListItem,
    BlogPostPublicResponse,
    BlogPostUpdateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/blog", tags=["blog"])


# ── Public endpoints (no auth) ────────────────────────────────────────────────

@router.get("/posts", response_model=list[BlogPostListItem])
async def list_published_posts(db: AsyncSession = Depends(get_db)):
    """Return all published posts ordered by published_at desc."""
    result = await db.execute(
        select(BlogPostTable)
        .where(BlogPostTable.is_published.is_(True))
        .order_by(BlogPostTable.published_at.desc())
    )
    return result.scalars().all()


@router.get("/posts/{slug}", response_model=BlogPostPublicResponse)
async def get_post_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """Return a single published post by slug. 404 if not found or not published."""
    result = await db.execute(
        select(BlogPostTable).where(
            BlogPostTable.slug == slug,
            BlogPostTable.is_published.is_(True),
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# ── Admin endpoints (super user only) ────────────────────────────────────────

@router.get("/admin/posts", response_model=list[BlogPostAdminResponse])
async def admin_list_posts(
    db: AsyncSession = Depends(get_db),
    _: UsersTable = Depends(require_super_user),
):
    """List all posts (draft + published) ordered by created_at desc."""
    result = await db.execute(
        select(BlogPostTable).order_by(BlogPostTable.created_at.desc())
    )
    return result.scalars().all()


@router.get("/admin/posts/{post_id}", response_model=BlogPostAdminResponse)
async def admin_get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: UsersTable = Depends(require_super_user),
):
    """Fetch a single post by ID (for the edit page)."""
    result = await db.execute(
        select(BlogPostTable).where(BlogPostTable.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/admin/posts", response_model=BlogPostAdminResponse, status_code=201)
async def admin_create_post(
    body: BlogPostCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: UsersTable = Depends(require_super_user),
):
    """Create a new blog post (draft by default)."""
    existing = await db.execute(
        select(BlogPostTable.id).where(BlogPostTable.slug == body.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")

    post = BlogPostTable(
        slug=body.slug,
        title=body.title,
        excerpt=body.excerpt,
        content=body.content,
        category=body.category,
        read_time_minutes=body.read_time_minutes,
        author_name=body.author_name,
        is_published=False,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.put("/admin/posts/{post_id}", response_model=BlogPostAdminResponse)
async def admin_update_post(
    post_id: int,
    body: BlogPostUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: UsersTable = Depends(require_super_user),
):
    """Update fields on an existing post."""
    result = await db.execute(
        select(BlogPostTable).where(BlogPostTable.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = body.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != post.slug:
        conflict = await db.execute(
            select(BlogPostTable.id).where(BlogPostTable.slug == update_data["slug"])
        )
        if conflict.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Slug already exists")

    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/admin/posts/{post_id}", status_code=204)
async def admin_delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: UsersTable = Depends(require_super_user),
):
    """Hard delete a post."""
    result = await db.execute(
        select(BlogPostTable).where(BlogPostTable.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    await db.commit()


@router.post("/admin/posts/{post_id}/publish", response_model=BlogPostAdminResponse)
async def admin_toggle_publish(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: UsersTable = Depends(require_super_user),
):
    """Toggle is_published. Sets published_at on first publish; clears on unpublish."""
    result = await db.execute(
        select(BlogPostTable).where(BlogPostTable.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.is_published = not post.is_published
    if post.is_published and post.published_at is None:
        post.published_at = datetime.now(timezone.utc)
    elif not post.is_published:
        post.published_at = None

    await db.commit()
    await db.refresh(post)
    return post
