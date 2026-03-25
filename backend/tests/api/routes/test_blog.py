"""Tests for the public blog and admin blog API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.db import get_db
from app.api.deps import get_current_user, require_super_user
from kila_models.models.database import BlogPostTable


@pytest.fixture(autouse=True)
def _cleanup_overrides():
    yield
    app.dependency_overrides.clear()


def _make_post(
    id=1,
    slug="test-post",
    title="Test Post",
    excerpt="An excerpt",
    content="# Hello\nContent here.",
    category="GEO",
    read_time_minutes=5,
    author_name="Kila Team",
    is_published=True,
    published_at=None,
) -> BlogPostTable:
    post = MagicMock(spec=BlogPostTable)
    post.id = id
    post.slug = slug
    post.title = title
    post.excerpt = excerpt
    post.content = content
    post.category = category
    post.read_time_minutes = read_time_minutes
    post.author_name = author_name
    post.is_published = is_published
    post.published_at = published_at or datetime(2026, 3, 25, tzinfo=timezone.utc)
    post.created_at = datetime(2026, 3, 25, tzinfo=timezone.utc)
    post.updated_at = None
    return post


def _mock_user():
    from kila_models.models.database import UsersTable
    user = MagicMock(spec=UsersTable)
    user.user_id = "user_123"
    return user


# ── Public endpoints ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_published_posts_returns_only_published():
    """GET /api/v1/blog/posts returns only published posts."""
    published_post = _make_post(id=1, slug="published", is_published=True)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [published_post]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/blog/posts")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "published"


@pytest.mark.asyncio
async def test_get_post_by_slug_404_for_draft():
    """GET /api/v1/blog/posts/{slug} returns 404 for unpublished/missing post."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/blog/posts/some-draft-post")

    assert response.status_code == 404


# ── Admin endpoints ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_create_post_requires_super_user():
    """POST /api/v1/blog/admin/posts returns 403 for non-super-user."""
    from fastapi import HTTPException

    app.dependency_overrides[require_super_user] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Admin access required")
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/blog/admin/posts",
            json={
                "slug": "new-post",
                "title": "New Post",
                "excerpt": "An excerpt",
                "content": "Content",
                "category": "GEO",
                "read_time_minutes": 5,
            },
            headers={"Authorization": "Bearer fake_token"},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_toggle_publish_sets_published_at():
    """POST /api/v1/blog/admin/posts/{id}/publish sets published_at on first publish."""
    mock_user = _mock_user()

    draft_post = _make_post(id=1, is_published=False, published_at=None)
    draft_post.published_at = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = draft_post

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    app.dependency_overrides[require_super_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/blog/admin/posts/1/publish",
            headers={"Authorization": "Bearer fake_token"},
        )

    assert response.status_code == 200
    assert draft_post.is_published is True
    assert draft_post.published_at is not None
