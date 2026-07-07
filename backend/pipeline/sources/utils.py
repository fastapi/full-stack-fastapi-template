from __future__ import annotations

import os
import re
from datetime import UTC, datetime

import httpx

from pipeline.utils import log

HN_PREFIX_RE = re.compile(r"^(?:Show|Launch|Ask|Tell) HN:\s*", re.IGNORECASE)
WINDOW_HOURS = 168
FETCH_TIMEOUT_SECS = 15.0
TAVILY_SEARCH_URL = "https://api.tavily.com/search"
TAVILY_SEARCH_CANDIDATES = 5
TWITTER_HOSTS = {"x.com", "twitter.com", "t.co"}
_TWITTER_HANDLE_PREFIX_RE = re.compile(r"^@\w+\s+[-–]\s+")

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def clean_title(title: str) -> str:
    return HN_PREFIX_RE.sub("", title).strip()


def is_within_window(date_str: str | None, window_hours: int = WINDOW_HOURS) -> bool:
    if not date_str:
        return True
    try:
        from email.utils import parsedate_to_datetime

        try:
            published = parsedate_to_datetime(date_str)
        except Exception:
            published = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        hours_ago = (now - published.astimezone(UTC)).total_seconds() / 3600
        return hours_ago <= window_hours
    except Exception:
        return True


def fetch_with_timeout(
    url: str,
    timeout: float = FETCH_TIMEOUT_SECS,
    proxy: str | None = None,
    headers: dict | None = None,
) -> httpx.Response:
    kwargs: dict = {"timeout": timeout, "follow_redirects": True}
    if proxy:
        kwargs["proxy"] = proxy
    if headers:
        kwargs["headers"] = headers
    with httpx.Client(**kwargs) as client:
        return client.get(url)


def tavily_search(query: str, max_results: int = TAVILY_SEARCH_CANDIDATES) -> list[dict]:
    api_key = os.environ["TAVILY_API_KEY"]
    resp = httpx.post(
        TAVILY_SEARCH_URL,
        json={"api_key": api_key, "query": query, "max_results": max_results},
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()
    return [
        {
            "title": r.get("title", ""),
            "url": r["url"],
            "description": r.get("content", ""),
        }
        for r in data.get("results", [])
    ]


def is_twitter_url(url: str) -> bool:
    try:
        from urllib.parse import urlparse

        return urlparse(url).hostname in TWITTER_HOSTS
    except Exception:
        return False


def resolve_twitter_url(title: str, description: str) -> str | None:
    """Given an x.com/twitter.com URL's title+description, search for the
    underlying article and return the best non-Twitter result URL.
    """
    clean = _TWITTER_HANDLE_PREFIX_RE.sub("", title).strip()
    first_sentence = description.split(". ")[0].strip() if description else ""
    query = f"{clean} {first_sentence}" if first_sentence else clean

    try:
        results = tavily_search(query)
    except Exception as e:
        log(f"    Search failed: {e}")
        return None

    match = next((r for r in results if not is_twitter_url(r["url"])), None)
    if match:
        log(f"    Resolved to: {match['url']}")
        return match["url"]
    return None
