import random

from sqlmodel import Session

from app.models_agentique import Article
from tests.utils.utils import random_lower_string


def create_random_article(db: Session, **overrides: object) -> Article:
    defaults: dict[str, object] = {
        "title": random_lower_string(),
        "source": "Hacker News",
        "source_type": "hackerNews",
        "url": f"https://example.com/{random_lower_string()}",
        "score": random.randint(1, 10),
        "summary": random_lower_string(),
        "categories": ["dev"],
        "kind": "blog",
        "content": random_lower_string(),
    }
    defaults.update(overrides)
    article = Article(**defaults)  # type: ignore[arg-type]
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
