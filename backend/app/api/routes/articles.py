from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Query
from model2vec import StaticModel
from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
from sqlalchemy import cast, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import col, select

from app.api.deps import SessionDep
from app.api.deps_agentique import CurrentUserOptional
from app.models_agentique import Article, ArticleLike, ArticlePublic, ArticlesPublic

router = APIRouter(prefix="/articles", tags=["articles"])

# Loaded once at module import — model2vec is CPU-only and tiny (~30 MB)
_model: StaticModel | None = None


def get_model() -> StaticModel:  # pragma: no cover
    global _model
    if _model is None:
        _model = StaticModel.from_pretrained("minishlab/potion-base-8M")
    return _model


def _embed(text: str) -> list[float]:  # pragma: no cover
    import numpy as np

    model = get_model()
    vec = model.encode([text])[0]
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def _liked_article_ids(session: SessionDep, user_id: Any) -> set[int]:
    return set(
        session.exec(
            select(ArticleLike.article_id).where(ArticleLike.user_id == user_id)
        ).all()
    )


def _like_counts_subquery() -> Any:
    return (
        select(ArticleLike.article_id, func.count().label("like_count"))
        .group_by(ArticleLike.article_id)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        .subquery()
    )


@router.get("/", response_model=ArticlesPublic)
def read_articles(
    session: SessionDep,
    current_user: CurrentUserOptional,
    limit: int = Query(default=20, ge=1, le=50),
    since: str | None = None,
    min_score: int | None = Query(default=None, ge=1, le=10),
    category: str | None = None,
    kind: str | None = None,
    sort: str = Query(default="score-desc"),
) -> Any:
    since_dt: datetime
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            since_dt = datetime.now(UTC) - timedelta(days=30)
    else:
        since_dt = datetime.now(UTC) - timedelta(days=30)

    conditions = [
        Article.score.is_not(None),  # type: ignore[union-attr]  # ty: ignore[unresolved-attribute]
        col(Article.published_at) >= since_dt,
    ]
    if min_score is not None:
        conditions.append(Article.score >= min_score)  # type: ignore[operator]  # ty: ignore[unsupported-operator]
    if kind is not None:
        conditions.append(Article.kind == kind)
    if category is not None:
        conditions.append(
            cast(Article.categories, JSONB).contains([category])  # type: ignore[arg-type]
        )

    count_statement = select(func.count()).select_from(Article).where(*conditions)
    count = session.exec(count_statement).one()

    like_counts_subq = _like_counts_subquery()
    like_count_expr = func.coalesce(like_counts_subq.c.like_count, 0)
    joined_statement = (
        select(Article, like_count_expr.label("like_count"))
        .outerjoin(like_counts_subq, like_counts_subq.c.article_id == Article.id)
        .where(*conditions)
    )

    if sort == "published_at-desc":
        joined_statement = joined_statement.order_by(
            col(Article.published_at).desc(), col(Article.id).desc()
        )
    elif sort == "likes-desc":
        joined_statement = joined_statement.order_by(
            like_count_expr.desc(), col(Article.score).desc(), col(Article.id).desc()
        )
    else:
        joined_statement = joined_statement.order_by(
            col(Article.score).desc(), col(Article.id).desc()
        )
    joined_statement = joined_statement.limit(limit)

    rows = session.exec(joined_statement).all()

    liked_ids = _liked_article_ids(session, current_user.id) if current_user else set()

    data = []
    for article, like_count in rows:
        pub = ArticlePublic.model_validate(article)
        pub.like_count = like_count
        pub.liked_by_me = article.id in liked_ids
        data.append(pub)

    return ArticlesPublic(data=data, count=count)


@router.get("/search", response_model=ArticlesPublic)
def search_articles(
    session: SessionDep,
    current_user: CurrentUserOptional,
    q: str,
    limit: int = Query(default=20, ge=1, le=50),
) -> Any:
    query_vec = _embed(q)

    like_counts_subq = _like_counts_subquery()
    like_count_expr = func.coalesce(like_counts_subq.c.like_count, 0)

    statement = (
        select(Article, like_count_expr.label("like_count"))
        .outerjoin(like_counts_subq, like_counts_subq.c.article_id == Article.id)
        .where(Article.score.is_not(None))  # type: ignore[union-attr]  # ty: ignore[unresolved-attribute]
        .where(Article.embedding.is_not(None))  # type: ignore[union-attr]  # ty: ignore[unresolved-attribute]
        .order_by(
            cast(Article.embedding, Vector(256)).cosine_distance(query_vec),
            col(Article.id).desc(),
        )
        .limit(limit)
    )

    rows = session.exec(statement).all()

    liked_ids = _liked_article_ids(session, current_user.id) if current_user else set()

    data = []
    for article, like_count in rows:
        pub = ArticlePublic.model_validate(article)
        pub.like_count = like_count
        pub.liked_by_me = article.id in liked_ids
        data.append(pub)

    return ArticlesPublic(data=data, count=len(data))


@router.get("/stats")
def article_stats(session: SessionDep) -> Any:
    total = session.exec(select(func.count()).select_from(Article)).one()
    last = session.exec(
        select(func.max(Article.created_at))  # type: ignore[arg-type]
    ).one()
    return {"total": total, "lastUpdated": last.isoformat() if last else None}
