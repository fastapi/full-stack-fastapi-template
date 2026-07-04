import math
import random
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine
from app.models_agentique import Article, ArticleLike

# Fixed seed so local dev, CI, and the Playwright stack all get the same 50 rows.
SEED = 20260701

CATEGORIES = ["models", "dev", "research"]
KINDS = ["repo", "paper", "model", "blog", "product", "announcement"]
SOURCE_TYPES = ["aiNews", "rss", "hackerNews"]
SOURCES = ["AI News", "Hacker News", "The Batch", "Import AI", "Latent Space"]

EMBEDDING_DIM = 256
ARTICLE_COUNT = 50


def _normalized_embedding(rng: random.Random) -> list[float]:
    vec = [rng.gauss(0, 1) for _ in range(EMBEDDING_DIM)]
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec]


def _published_at(rng: random.Random, index: int) -> datetime:
    now = datetime.now(UTC)
    if index < 40:
        # bulk: today down to a week ago
        return now - timedelta(days=rng.uniform(0, 7))
    elif index < 48:
        # a week ago down to just under the 30-day default window
        return now - timedelta(days=rng.uniform(7, 30))
    else:
        # just past the default `since` window, to exercise it
        return now - timedelta(days=rng.uniform(31, 40))


def make_sample_articles() -> list[Article]:
    rng = random.Random(SEED)
    articles = []
    for i in range(ARTICLE_COUNT):
        categories = rng.sample(CATEGORIES, k=rng.choice([1, 2]))
        articles.append(
            Article(
                title=f"Sample article {i + 1}",
                source=rng.choice(SOURCES),
                source_type=rng.choice(SOURCE_TYPES),
                url=f"https://example.com/articles/{i + 1}",
                published_at=_published_at(rng, i),
                score=rng.randint(1, 10),
                summary=f"Summary for sample article {i + 1}.",
                categories=categories,
                kind=rng.choice(KINDS),
                content=f"Content body for sample article {i + 1}.",
                embedding=_normalized_embedding(rng),
            )
        )
    return articles


def seed(session: Session) -> None:
    # article_like FK-references article, so clear it before wiping articles.
    session.exec(delete(ArticleLike))
    session.exec(delete(Article))
    session.add_all(make_sample_articles())
    session.commit()


def main() -> None:
    if settings.ENVIRONMENT == "production":
        raise RuntimeError(
            "Refusing to run seed_articles in production; it wipes the articles table."
        )
    with Session(engine) as session:
        seed(session)


if __name__ == "__main__":
    main()
