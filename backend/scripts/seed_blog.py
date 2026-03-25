"""
Seed script: insert the GEO article as the first blog post.
Idempotent — skips if slug already exists.

Usage:
    cd kila/backend
    uv run python scripts/seed_blog.py
"""

import asyncio
import sys
from pathlib import Path

# Allow imports from app/
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("ENVIRONMENT", "development")

from datetime import datetime, timezone
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from kila_models.models.database import BlogPostTable


SLUG = "geo-generative-engine-optimization"
BLOG_POST_PATH = Path(__file__).parent.parent.parent.parent / "docs" / "blog-geo-generative-engine-optimization.md"

if not BLOG_POST_PATH.exists():
    raise FileNotFoundError(f"Blog post markdown not found at: {BLOG_POST_PATH.resolve()}")


def _read_content() -> str:
    """Read the markdown file and strip the final CTA line."""
    text = BLOG_POST_PATH.read_text(encoding="utf-8")
    lines = text.rstrip().splitlines()
    # Remove trailing separator and CTA (last lines: ---, blank, *Kila tracks...)
    while lines and (lines[-1].strip() == "" or lines[-1].strip() == "---" or lines[-1].startswith("*Kila")):
        lines.pop()
    return "\n".join(lines)


def _read_excerpt(content: str) -> str:
    """Use the first italic paragraph as excerpt."""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("*") and stripped.endswith("*"):
            return stripped.lstrip("*").rstrip("*").strip()
    return "For the past two decades, brands have poured billions into SEO. But a quiet shift is underway."


async def seed():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(BlogPostTable.id).where(BlogPostTable.slug == SLUG)
        )
        if result.scalar_one_or_none():
            print(f"Post '{SLUG}' already exists — skipping.")
            return

        content = _read_content()
        excerpt = _read_excerpt(content)

        post = BlogPostTable(
            slug=SLUG,
            title="GEO: Generative Engine Optimization — The New Frontier Every Brand Needs to Understand",
            excerpt=excerpt,
            content=content,
            category="GEO",
            read_time_minutes=8,
            author_name="Kila Team",
            is_published=True,
            published_at=datetime(2026, 3, 25, tzinfo=timezone.utc),
        )
        db.add(post)
        await db.commit()
        print(f"✓ Inserted post: '{SLUG}'")


if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except Exception as e:
        print(f"Seed failed: {e}")
        sys.exit(1)
