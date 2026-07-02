import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pgvector.sqlalchemy import Vector
from sqlalchemy import cast
from sqlmodel import Session, select

from app.api.routes import articles
from app.core.config import settings
from app.core.security import create_access_token
from app.models_agentique import Article
from tests.utils.article import create_random_article
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email

ARTICLES_URL = f"{settings.API_V1_STR}/articles"


def test_read_articles_default(client: TestClient) -> None:
    r = client.get(f"{ARTICLES_URL}/")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] > 0
    assert len(data["data"]) > 0
    article = data["data"][0]
    assert "title" in article
    assert "score" in article


def test_read_articles_filter_category(client: TestClient) -> None:
    r = client.get(f"{ARTICLES_URL}/", params={"category": "dev", "limit": 50})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] > 0
    assert all("dev" in a["categories"] for a in data["data"])


def test_read_articles_filter_min_score(client: TestClient) -> None:
    r = client.get(f"{ARTICLES_URL}/", params={"min_score": 8, "limit": 50})
    assert r.status_code == 200
    data = r.json()
    assert all(a["score"] >= 8 for a in data["data"])


def test_read_articles_filter_kind(client: TestClient) -> None:
    r = client.get(f"{ARTICLES_URL}/", params={"kind": "repo", "limit": 50})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] > 0
    assert all(a["kind"] == "repo" for a in data["data"])


def test_read_articles_filter_never_increases_count(client: TestClient) -> None:
    base = client.get(f"{ARTICLES_URL}/").json()["count"]
    filtered = client.get(f"{ARTICLES_URL}/", params={"min_score": 5}).json()["count"]
    assert filtered <= base


def test_read_articles_sort_published_at_desc(client: TestClient) -> None:
    r = client.get(
        f"{ARTICLES_URL}/", params={"sort": "published_at-desc", "limit": 50}
    )
    data = r.json()["data"]
    dates = [datetime.fromisoformat(a["published_at"]) for a in data]
    assert dates == sorted(dates, reverse=True)


def test_read_articles_sort_default_is_score_desc(client: TestClient) -> None:
    r = client.get(f"{ARTICLES_URL}/", params={"limit": 50})
    scores = [a["score"] for a in r.json()["data"]]
    assert scores == sorted(scores, reverse=True)


def test_read_articles_since_narrows_results(client: TestClient) -> None:
    wide_since = (datetime.now(UTC) - timedelta(days=30)).isoformat()
    narrow_since = (datetime.now(UTC) - timedelta(days=3)).isoformat()

    wide = client.get(
        f"{ARTICLES_URL}/", params={"since": wide_since, "limit": 50}
    ).json()
    narrow = client.get(
        f"{ARTICLES_URL}/", params={"since": narrow_since, "limit": 50}
    ).json()

    assert narrow["count"] <= wide["count"]
    narrow_ids = {a["id"] for a in narrow["data"]}
    wide_ids = {a["id"] for a in wide["data"]}
    assert narrow_ids <= wide_ids


def test_read_articles_malformed_since_falls_back_to_default_window(
    client: TestClient,
) -> None:
    default = client.get(f"{ARTICLES_URL}/").json()
    malformed = client.get(f"{ARTICLES_URL}/", params={"since": "not-a-date"}).json()

    assert malformed["count"] == default["count"]


def test_search_articles(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_vec = [0.05] * 256
    monkeypatch.setattr(articles, "_embed", lambda text: fake_vec)

    r = client.get(f"{ARTICLES_URL}/search", params={"q": "agents", "limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) <= 5
    assert data["count"] == len(data["data"])

    expected_ids = db.exec(
        select(Article.id)
        .where(Article.score.is_not(None))  # type: ignore[union-attr]
        .where(Article.embedding.is_not(None))  # type: ignore[union-attr]
        .order_by(cast(Article.embedding, Vector(256)).cosine_distance(fake_vec))
        .limit(5)
    ).all()
    assert [a["id"] for a in data["data"]] == list(expected_ids)


def test_article_stats(client: TestClient) -> None:
    r = client.get(f"{ARTICLES_URL}/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 50
    datetime.fromisoformat(data["lastUpdated"])


def test_read_articles_anonymous_has_like_count_and_liked_by_me(
    client: TestClient,
) -> None:
    r = client.get(f"{ARTICLES_URL}/", params={"limit": 50})
    data = r.json()["data"]
    assert len(data) > 0
    for article in data:
        assert article["like_count"] >= 0
        assert article["liked_by_me"] is False


def test_read_articles_liked_by_me_true_only_for_liked(
    client: TestClient, db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    now = datetime.now(UTC)
    liked = create_random_article(db, score=9, published_at=now)
    unliked = create_random_article(db, score=9, published_at=now)

    r = client.put(f"{ARTICLES_URL}/{liked.id}/like", headers=normal_user_token_headers)
    assert r.status_code == 200

    r = client.get(
        f"{ARTICLES_URL}/", params={"limit": 50}, headers=normal_user_token_headers
    )
    data = {a["id"]: a for a in r.json()["data"]}
    assert data[liked.id]["liked_by_me"] is True
    assert data[liked.id]["like_count"] == 1
    assert data[unliked.id]["liked_by_me"] is False
    assert data[unliked.id]["like_count"] == 0


def test_read_articles_garbage_token_treated_as_anonymous(client: TestClient) -> None:
    r = client.get(
        f"{ARTICLES_URL}/",
        params={"limit": 5},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert r.status_code == 200
    for article in r.json()["data"]:
        assert article["liked_by_me"] is False


def test_read_articles_valid_token_unknown_user_treated_as_anonymous(
    client: TestClient,
) -> None:
    token = create_access_token(str(uuid.uuid4()), expires_delta=timedelta(minutes=5))
    r = client.get(
        f"{ARTICLES_URL}/",
        params={"limit": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    for article in r.json()["data"]:
        assert article["liked_by_me"] is False


def test_read_articles_sort_likes_desc(client: TestClient, db: Session) -> None:
    now = datetime.now(UTC)
    low_score_more_likes = create_random_article(db, score=3, published_at=now)
    high_score_no_likes = create_random_article(db, score=9, published_at=now)
    tied_score_a = create_random_article(db, score=5, published_at=now)
    tied_score_b = create_random_article(db, score=5, published_at=now)

    headers_list = [
        authentication_token_from_email(client=client, email=random_email(), db=db)
        for _ in range(2)
    ]
    for headers in headers_list:
        client.put(f"{ARTICLES_URL}/{low_score_more_likes.id}/like", headers=headers)
    client.put(f"{ARTICLES_URL}/{tied_score_a.id}/like", headers=headers_list[0])

    r = client.get(f"{ARTICLES_URL}/", params={"sort": "likes-desc", "limit": 50})
    data = r.json()["data"]
    ids = [a["id"] for a in data]

    assert ids.index(low_score_more_likes.id) < ids.index(high_score_no_likes.id)
    # tied like counts (both 0) fall back to score desc
    assert ids.index(high_score_no_likes.id) < ids.index(tied_score_b.id)
    # tied_score_a has 1 like, tied_score_b has 0 -> a before b despite equal score
    assert ids.index(tied_score_a.id) < ids.index(tied_score_b.id)


def test_search_articles_has_like_count_and_liked_by_me(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_vec = [0.05] * 256
    monkeypatch.setattr(articles, "_embed", lambda text: fake_vec)

    r = client.get(f"{ARTICLES_URL}/search", params={"q": "agents", "limit": 5})
    assert r.status_code == 200
    for article in r.json()["data"]:
        assert "like_count" in article
        assert "liked_by_me" in article
