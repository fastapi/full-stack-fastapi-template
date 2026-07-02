from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import settings
from app.models_agentique import ArticleLike
from tests.utils.article import create_random_article
from tests.utils.user import authentication_token_from_email, create_random_user
from tests.utils.utils import random_email


def test_article_like_duplicate_pk_raises(db: Session) -> None:
    user = create_random_user(db)
    article = create_random_article(db)
    assert user.id is not None
    assert article.id is not None

    db.add(ArticleLike(user_id=user.id, article_id=article.id))
    db.commit()

    db.add(ArticleLike(user_id=user.id, article_id=article.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_article_like_created_at_auto_populates(db: Session) -> None:
    user = create_random_user(db)
    article = create_random_article(db)
    assert user.id is not None
    assert article.id is not None

    like = ArticleLike(user_id=user.id, article_id=article.id)
    db.add(like)
    db.commit()
    db.refresh(like)

    assert isinstance(like.created_at, datetime)


def test_like_without_token_returns_401(client: TestClient, db: Session) -> None:
    article = create_random_article(db)
    r = client.put(f"{settings.API_V1_STR}/articles/{article.id}/like")
    assert r.status_code == 401


def test_like_with_token_creates_row(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    article = create_random_article(db)
    r = client.put(
        f"{settings.API_V1_STR}/articles/{article.id}/like",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200

    rows = db.exec(
        select(ArticleLike).where(ArticleLike.article_id == article.id)
    ).all()
    assert len(rows) == 1


def test_like_is_idempotent(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    article = create_random_article(db)
    for _ in range(3):
        r = client.put(
            f"{settings.API_V1_STR}/articles/{article.id}/like",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200

    rows = db.exec(
        select(ArticleLike).where(ArticleLike.article_id == article.id)
    ).all()
    assert len(rows) == 1


def test_like_nonexistent_article_404(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.put(
        f"{settings.API_V1_STR}/articles/999999999/like",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404

    rows = db.exec(select(ArticleLike).where(ArticleLike.article_id == 999999999)).all()
    assert len(rows) == 0


def test_unlike_removes_row(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    article = create_random_article(db)
    client.put(
        f"{settings.API_V1_STR}/articles/{article.id}/like",
        headers=normal_user_token_headers,
    )

    r = client.delete(
        f"{settings.API_V1_STR}/articles/{article.id}/like",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200

    rows = db.exec(
        select(ArticleLike).where(ArticleLike.article_id == article.id)
    ).all()
    assert len(rows) == 0


def test_unlike_when_not_liked_is_idempotent(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    article = create_random_article(db)
    r = client.delete(
        f"{settings.API_V1_STR}/articles/{article.id}/like",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200


def test_liked_articles_without_token_returns_401(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/me/liked-articles")
    assert r.status_code == 401


def test_liked_articles_ordered_newest_liked_first(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    articles = [create_random_article(db) for _ in range(3)]
    for article in articles:
        r = client.put(
            f"{settings.API_V1_STR}/articles/{article.id}/like",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200

    r = client.get(
        f"{settings.API_V1_STR}/me/liked-articles", headers=normal_user_token_headers
    )
    assert r.status_code == 200
    data = r.json()["data"]
    returned_ids = [a["id"] for a in data]
    liked_ids = [a.id for a in reversed(articles)]
    assert returned_ids[: len(liked_ids)] == liked_ids


def test_liked_articles_have_correct_like_count_and_liked_by_me(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    article = create_random_article(db)
    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    client.put(
        f"{settings.API_V1_STR}/articles/{article.id}/like", headers=other_headers
    )
    client.put(
        f"{settings.API_V1_STR}/articles/{article.id}/like",
        headers=normal_user_token_headers,
    )

    r = client.get(
        f"{settings.API_V1_STR}/me/liked-articles", headers=normal_user_token_headers
    )
    assert r.status_code == 200
    data = {a["id"]: a for a in r.json()["data"]}
    assert data[article.id]["liked_by_me"] is True
    assert data[article.id]["like_count"] == 2


def test_liked_articles_does_not_leak_other_users_likes(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    my_article = create_random_article(db)
    other_article = create_random_article(db)

    client.put(
        f"{settings.API_V1_STR}/articles/{my_article.id}/like",
        headers=normal_user_token_headers,
    )

    other_headers = authentication_token_from_email(
        client=client, email=random_email(), db=db
    )
    client.put(
        f"{settings.API_V1_STR}/articles/{other_article.id}/like",
        headers=other_headers,
    )

    r = client.get(
        f"{settings.API_V1_STR}/me/liked-articles", headers=normal_user_token_headers
    )
    returned_ids = {a["id"] for a in r.json()["data"]}
    assert my_article.id in returned_ids
    assert other_article.id not in returned_ids
