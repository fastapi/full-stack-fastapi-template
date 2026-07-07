"""Pipeline entry point. Run with: python -m pipeline.run"""

from __future__ import annotations

import os
import sys
import time
from datetime import UTC, datetime, timedelta

from model2vec import StaticModel
from sqlmodel import Session, create_engine, select

from app.models_agentique import Article, ScoredUrl
from baml_client.sync_client import b
from baml_client.types import ArticleInput, ExistingArticle
from pipeline.sources.ainews import fetch_ai_news
from pipeline.sources.email import fetch_newsletter
from pipeline.sources.extract_content import re_extract_full_content
from pipeline.sources.hn import fetch_hn
from pipeline.sources.substack import fetch_substack
from pipeline.steps import (
    PROMPT_CONTENT_CAP,
    SCORE_THRESHOLD,
    TRUST_BY_SOURCE,
    github_repo_from_content,
    kind_from_url,
)
from pipeline.utils import log, sanitize_llm_text, strip_title_wrappers, wait_ms


def _build_db_url() -> str:
    server = os.environ["POSTGRES_SERVER"]
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ["POSTGRES_USER"]
    password = os.environ.get("POSTGRES_PASSWORD", "")
    db = os.environ.get("POSTGRES_DB", "")
    return f"postgresql+psycopg://{user}:{password}@{server}:{port}/{db}"


_engine = create_engine(_build_db_url())

_model: StaticModel | None = None


def _get_model() -> StaticModel:
    global _model
    if _model is None:
        _model = StaticModel.from_pretrained("minishlab/potion-base-8M")
    return _model


def _embed(text: str) -> list[float]:
    return _get_model().encode([text])[0].tolist()


SOURCES = [
    {"label": "Hacker News", "fetcher": fetch_hn},
    {"label": "Newsletter", "fetcher": fetch_newsletter},
    {"label": "AI News", "fetcher": fetch_ai_news},
    {"label": "Substack", "fetcher": fetch_substack},
]


def _to_baml_input(a: dict) -> ArticleInput:
    """Build a BAML ArticleInput from a fetched-article dict (snippet capped at 200)."""
    return ArticleInput(
        url=a["url"],
        title=a["title"],
        source=a["source"],
        snippet=a.get("content", "")[:200] if a.get("content") else None,
        trust=TRUST_BY_SOURCE.get(a["source"]),
    )


def run_pipeline() -> None:
    log("=== Pipeline start ===")
    start = time.time()

    with Session(_engine) as session:
        for src in SOURCES:
            log(f"\n=== Processing {src['label']} ===")

            fetched = _fetch_source(src["fetcher"], src["label"])
            fresh = _filter_known_urls(session, fetched, src["label"])
            alive = _filter_dead_domains(fresh, src["label"])
            unique = _dedup_semantic(session, alive, src["label"])
            scored = _score_articles(session, unique)
            inserted = _insert_articles(session, scored)
            _improve_titles(session, inserted)
            with_content = _extract_full_content(session, inserted)
            processed = _summarize_and_categorize(session, with_content)
            _embed_articles(session, processed)

    elapsed = f"{time.time() - start:.1f}"
    log(f"=== Pipeline complete in {elapsed}s ===")


# ─── Step 01 ────────────────────────────────────────────────────────────────


def _fetch_source(fetcher, label: str) -> list[dict]:
    articles = fetcher()
    if not articles:
        log(f"No articles from {label}")
    return articles


# ─── Step 02 ────────────────────────────────────────────────────────────────


def _filter_known_urls(
    session: Session, articles: list[dict], label: str
) -> list[dict]:
    if not articles:
        return []
    all_urls = [a["url"] for a in articles]

    existing_urls = set(
        session.exec(select(Article.url).where(Article.url.in_(all_urls))).all()
    )
    scored_urls = set(
        session.exec(select(ScoredUrl.url).where(ScoredUrl.url.in_(all_urls))).all()
    )

    fresh = [
        a
        for a in articles
        if a["url"] not in existing_urls and a["url"] not in scored_urls
    ]

    if existing_urls or scored_urls:
        log(
            f"  Filtered {len(existing_urls)} known + {len(scored_urls)} already-scored URLs"
        )
    if not fresh:
        log(f"  No new articles from {label}")
        return []
    log(f"  {len(fresh)} new articles to process")
    return fresh


# ─── Step 02b ───────────────────────────────────────────────────────────────


def _filter_dead_domains(articles: list[dict], label: str) -> list[dict]:
    if not articles:
        return articles

    from urllib.parse import urlparse

    import dns.resolver

    def is_resolvable(url: str) -> bool:
        try:
            host = urlparse(url).hostname
            if not host:
                return False
            dns.resolver.resolve(host, "A")
            return True
        except dns.resolver.NXDOMAIN:
            return False
        except Exception:
            return True  # Other errors (timeout, etc.) - assume alive

    results = [(a, is_resolvable(a["url"])) for a in articles]
    alive = [a for a, ok in results if ok]
    dead = [a for a, ok in results if not ok]
    for a in dead:
        log(f"  Dropped dead URL: {a['url']}")
    if dead:
        log(f"  Filtered {len(dead)} dead-domain URLs from {label}")
    return alive


# ─── Step 03 ────────────────────────────────────────────────────────────────


def _dedup_semantic(session: Session, articles: list[dict], label: str) -> list[dict]:
    if not articles:
        return articles

    cutoff = datetime.now(UTC) - timedelta(days=14)
    recent_db = session.exec(
        select(Article).where(Article.published_at >= cutoff)
    ).all()

    if not recent_db:
        return articles

    log(f"  Deduplicating against {len(recent_db)} recent DB articles...")

    new_inputs = [_to_baml_input(a) for a in articles]
    existing_inputs = [
        ExistingArticle(url=str(art.url), title=art.title, source=art.source)
        for art in recent_db
    ]

    try:
        matches = b.SemanticDedup(new_inputs, existing_inputs)
        merged_urls = {m.url for m in matches}
        for m in matches:
            log(f"  Dropped duplicate: {m.url} (matches existing: {m.existingUrl})")
        if merged_urls:
            log(f"  {len(merged_urls)} articles dropped as duplicates")
        unique = [a for a in articles if a["url"] not in merged_urls]
        if not unique:
            log(f"  No new unique articles from {label}")
        return unique
    except Exception as e:
        log(f"  Dedup failed, continuing without: {e}")
        return articles


# ─── Step 04 ────────────────────────────────────────────────────────────────


def _score_articles(session: Session, articles: list[dict]) -> list[dict]:
    if not articles:
        return []

    log(f"  Scoring {len(articles)} articles in batches of 5...")

    BATCH = 5
    all_scores: list[dict] = []
    for i in range(0, len(articles), BATCH):
        batch_inputs = [_to_baml_input(a) for a in articles[i : i + BATCH]]
        result = b.ScoreArticles(batch_inputs)
        all_scores.extend({"url": r.url, "score": r.score} for r in result)
        log(f"    batch {i // BATCH + 1}/{(len(articles) + BATCH - 1) // BATCH} done")
        wait_ms(1000)

    score_by_url = {s["url"]: s["score"] for s in all_scores}
    scored = []
    for a in articles:
        score = score_by_url.get(a["url"], 0)
        if a["source"] == "Ben's Bites":
            score = min(score + 10, 100)
        scored.append({**a, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    kept = [s for s in scored if s["score"] >= SCORE_THRESHOLD]
    log(f"  {len(kept)} articles pass scoring (threshold: {SCORE_THRESHOLD})")

    # Record ALL evaluated URLs (including sub-threshold)
    for a in articles:
        session.merge(ScoredUrl(url=a["url"]))
    session.commit()

    return kept


# ─── Step 05 ────────────────────────────────────────────────────────────────


def _insert_articles(session: Session, scored: list[dict]) -> list[dict]:
    if not scored:
        return []

    by_url: dict[str, dict] = {}
    for item in scored:
        existing = by_url.get(item["url"])
        if not existing or item["score"] > existing["score"]:
            by_url[item["url"]] = item

    inserted = []
    for item in by_url.values():
        item["title"] = sanitize_llm_text(item["title"])
        pub_at = None
        if item.get("published_date"):
            try:
                from email.utils import parsedate_to_datetime

                try:
                    pub_at = parsedate_to_datetime(item["published_date"])
                except Exception:
                    pub_at = datetime.fromisoformat(
                        item["published_date"].replace("Z", "+00:00")
                    )
            except Exception:
                pass

        article = Article(
            title=item["title"],
            source=item["source"],
            source_type=item["source_type"],
            url=item["url"],
            published_at=pub_at,
            score=item["score"],
            content=item.get("content") or "",
        )
        session.add(article)
        session.flush()
        assert article.id is not None
        log(f"  Inserted #{article.id}: [{item['score']}/100] {item['title']}")
        inserted.append({**item, "id": article.id})

    session.commit()
    return inserted


# ─── Step 06 ────────────────────────────────────────────────────────────────


def _improve_titles(session: Session, inserted: list[dict]) -> None:
    if not inserted:
        return

    log(f"  Improving {len(inserted)} titles...")

    for item in inserted:
        art_id = item["id"]
        try:
            fixes = b.ImproveTitles([_to_baml_input(item)])
            raw = fixes[0].title if fixes else None
            if not raw:
                continue
            sanitized = sanitize_llm_text(strip_title_wrappers(raw))
            if not sanitized or sanitized == item["title"]:
                continue
            if item["source"].lower() in sanitized.lower():
                log(f'  Skip rewrite #{art_id} (source name leaked): "{sanitized}"')
                continue
            old_title = item["title"]
            article = session.get(Article, art_id)
            if article:
                article.title = sanitized
                session.add(article)
                session.commit()
            item["title"] = sanitized
            log(f'  Improved title #{art_id}: "{old_title}" → "{sanitized}"')
        except Exception as e:
            log(f"  Title improve failed for #{art_id}, continuing: {e}")


# ─── Step 07 ────────────────────────────────────────────────────────────────


def _extract_full_content(session: Session, inserted: list[dict]) -> list[dict]:
    if not inserted:
        return []

    to_extract = [a for a in inserted if a["source_type"] not in ("aiNews", "rss")]
    content_map = re_extract_full_content([{"url": a["url"]} for a in to_extract])

    for item in to_extract:
        full = content_map.get(item["url"])
        if full:
            article = session.get(Article, item["id"])
            if article:
                article.content = full
                session.add(article)
    session.commit()

    result = []
    for item in inserted:
        if item["source_type"] in ("aiNews", "rss"):
            result.append({**item, "full_content": item.get("content", "")})
        else:
            result.append({**item, "full_content": content_map.get(item["url"], "")})
    return result


# ─── Step 08 ────────────────────────────────────────────────────────────────


def _summarize_and_categorize(session: Session, items: list[dict]) -> list[dict]:
    if not items:
        return []

    log(f"  Summarizing and categorizing {len(items)} articles...")
    processed = []

    for item in items:
        art_id = item["id"]
        full_content = item.get("full_content", "")
        summary = ""
        categories: list[str] = []
        kind: str | None = kind_from_url(item["url"])

        try:
            if full_content:
                result = b.SummarizeAndCategorize(
                    item["title"], full_content[:PROMPT_CONTENT_CAP]
                )
                summary = sanitize_llm_text(result.summary or "")
                categories = [c.lower() for c in result.categories]
                if not kind:
                    kind = result.kind.value.lower()
                if kind == "blog" and github_repo_from_content(full_content):
                    kind = "repo"
            else:
                result = b.CategorizeOnly(item["title"])
                categories = [c.lower() for c in result.categories]
                if not kind:
                    kr = b.ClassifyKind(item["title"], item["url"], None)
                    kind = kr.kind.value.lower()
        except Exception as e:
            log(f"  Summarize/categorize failed for #{art_id}: {e}")

        article = session.get(Article, art_id)
        if article:
            article.summary = summary
            article.categories = categories
            if kind:
                article.kind = kind
            session.add(article)

        processed.append(
            {
                "id": art_id,
                "url": item["url"],
                "title": item["title"],
                "score": item["score"],
                "summary": summary,
                "categories": categories,
            }
        )

    session.commit()
    log("  Done summarizing and categorizing")
    return processed


# ─── Step 09 ────────────────────────────────────────────────────────────────


def _embed_articles(session: Session, items: list[dict]) -> None:
    if not items:
        return

    log(f"  Embedding {len(items)} articles...")

    for item in items:
        art_id = item["id"]
        try:
            text = (
                f"{item['title']}\n\n{item['summary']}"
                if item.get("summary")
                else item["title"]
            )
            vec = _embed(text)
            article = session.get(Article, art_id)
            if article:
                article.embedding = vec
                session.add(article)
        except Exception as e:
            log(f"  Embed failed for #{art_id}: {e}")

    session.commit()


# ─── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        run_pipeline()
        sys.exit(0)
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        raise
        sys.exit(1)
