"""Generic multi-feed RSS source. Not wired into SOURCES by default (see
run.py) - it wasn't active in the original TS pipeline either.
"""

from __future__ import annotations

import feedparser

from pipeline.sources.utils import (
    clean_title,
    fetch_with_timeout,
    is_twitter_url,
    is_within_window,
    resolve_twitter_url,
)
from pipeline.utils import log

SOURCES = [
    # Only ingest these RSS categories - others are noise (drama, events, business, etc.).
    {
        "name": "Aligned News",
        "rss_url": "https://alignednews.com/feed.xml",
        "allowed_categories": {"tips", "products"},
    },
    # Newsletters that publish an RSS feed - moved here from the IMAP-based
    # Newsletter source (pipeline/sources/email.py) since reading the feed
    # directly is simpler and doesn't need a mailbox. No category filter -
    # take everything within the recency window, same as substack.py/hn.py.
    {"name": "Console", "rss_url": "https://console.dev/rss.xml"},
    {"name": "The Neuron", "rss_url": "https://rss.beehiiv.com/feeds/N4eCstxvgX.xml"},
    {"name": "AI Hero", "rss_url": "https://www.aihero.dev/rss.xml"},
    {"name": "Import AI", "rss_url": "https://importai.substack.com/feed"},
    {"name": "TLDR AI", "rss_url": "https://tldr.tech/api/rss/ai"},
    {"name": "The Rundown AI", "rss_url": "https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml"},
    # Ben's Bites is deliberately not here: it's already covered by
    # substack-sources.json / fetch_substack(), which is wired into SOURCES.
    # Adding it here too would fetch the same feed twice per run.
]

USER_AGENT = "Agentique/2.0 (+https://agentique.ch)"


def _entry_categories(entry: dict) -> list[str]:
    tags = entry.get("tags")
    if tags:
        return [t.get("term", "") for t in tags if t.get("term")]
    category = entry.get("category")
    return [category] if category else []


def fetch_rss() -> list[dict]:
    articles: list[dict] = []

    for source in SOURCES:
        log(f"Fetching {source['name']}...")
        try:
            resp = fetch_with_timeout(source["rss_url"], headers={"User-Agent": USER_AGENT})
            if not resp.is_success:
                raise ValueError(f"Status {resp.status_code}")
            feed = feedparser.parse(resp.content)
        except Exception as e:
            log(f"  FAILED: {e}")
            continue

        within_window = [
            e for e in feed.entries if is_within_window(e.get("published"))
        ]

        allowed_categories = source.get("allowed_categories")
        if allowed_categories is None:
            relevant = within_window
        else:
            relevant = [
                e
                for e in within_window
                if any(c.lower() in allowed_categories for c in _entry_categories(e))
            ]

        log(
            f"  {source['name']}: {len(within_window)} in window, "
            f"{len(relevant)} after category filter"
        )

        for entry in relevant:
            raw_url = entry.get("link", "")
            description = entry.get("summary", "")
            title = clean_title(entry.get("title", "(no title)"))

            url = raw_url
            if is_twitter_url(raw_url):
                log(f"    Resolving tweet: {title}")
                found = resolve_twitter_url(title, description)
                if found:
                    url = found

            articles.append(
                {
                    "title": title,
                    "url": url,
                    # RSS description is a quality AI summary, far better than
                    # what scraping x.com would return.
                    "content": description,
                    "published_date": entry.get("published"),
                    "source": source["name"],
                    "source_type": "rss",
                }
            )

        log(f"  {source['name']}: {len(articles)} articles ready")

    log(f"RSS: {len(articles)} articles")
    return articles
