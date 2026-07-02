from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep
from app.models_agentique import Article, ArticleLike, ArticlePublic, ArticlesPublic

router = APIRouter(tags=["likes"])


@router.put("/articles/{article_id}/like")
def like_article(
    session: SessionDep, current_user: CurrentUser, article_id: int
) -> Any:
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    existing = session.get(ArticleLike, (current_user.id, article_id))
    if not existing:
        session.add(ArticleLike(user_id=current_user.id, article_id=article_id))
        session.commit()

    return {"ok": True}


@router.delete("/articles/{article_id}/like")
def unlike_article(
    session: SessionDep, current_user: CurrentUser, article_id: int
) -> Any:
    existing = session.get(ArticleLike, (current_user.id, article_id))
    if existing:
        session.delete(existing)
        session.commit()

    return {"ok": True}


@router.get("/me/liked-articles", response_model=ArticlesPublic)
def read_liked_articles(session: SessionDep, current_user: CurrentUser) -> Any:
    like_counts_subq = (
        select(ArticleLike.article_id, func.count().label("like_count"))
        .group_by(ArticleLike.article_id)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        .subquery()
    )
    like_count_expr = func.coalesce(like_counts_subq.c.like_count, 0)

    statement = (
        select(Article, like_count_expr.label("like_count"))
        .join(ArticleLike, col(ArticleLike.article_id) == col(Article.id))
        .outerjoin(like_counts_subq, like_counts_subq.c.article_id == Article.id)
        .where(ArticleLike.user_id == current_user.id)
        .order_by(col(ArticleLike.created_at).desc())
    )
    rows = session.exec(statement).all()

    data = []
    for article, like_count in rows:
        pub = ArticlePublic.model_validate(article)
        pub.like_count = like_count
        pub.liked_by_me = True
        data.append(pub)

    return ArticlesPublic(data=data, count=len(data))
