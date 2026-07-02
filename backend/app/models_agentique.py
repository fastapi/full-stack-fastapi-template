import uuid
from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


class ArticleBase(SQLModel):
    title: str
    source: str
    source_type: str
    url: str | None = None
    published_at: datetime | None = None
    score: int | None = None
    summary: str | None = None
    categories: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=True)
    )
    kind: str | None = None


class Article(ArticleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str | None = Field(default="")
    # 256-dim model2vec vectors; nullable until the import script runs
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(256), nullable=True)
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class ArticlePublic(ArticleBase):
    id: int
    created_at: datetime | None = None
    like_count: int = 0
    liked_by_me: bool = False


class ArticlesPublic(SQLModel):
    data: list[ArticlePublic]
    count: int


class ArticleLike(SQLModel, table=True):
    __tablename__ = "article_like"
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    article_id: int = Field(foreign_key="article.id", primary_key=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)


class ScoredUrl(SQLModel, table=True):
    __tablename__ = "scored_url"
    url: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)


class NewsletterSubscriber(SQLModel, table=True):
    __tablename__ = "newsletter_subscriber"
    email: str = Field(primary_key=True)
    categories: list[str] = Field(
        default_factory=lambda: ["all"], sa_column=Column(JSON, nullable=False)
    )
    custom_category: str = Field(default="")
    utm_source: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=get_datetime_utc)
    updated_at: datetime = Field(default_factory=get_datetime_utc)


class NewsletterSubscribeRequest(SQLModel):
    email: str
    categories: list[str] = Field(default_factory=lambda: ["all"])
    customCategory: str = ""
    utm_source: str | None = None


class NewsletterSubscribeResponse(SQLModel):
    ok: bool = True
