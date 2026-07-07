"""Newsletter (IMAP) pipeline source.

Reads unread emails from known newsletter senders in the "sub" mailbox,
extracts named products via BAML, and resolves each to a canonical URL via
web search. Newsletter links are tracking redirects, not trustworthy hrefs,
so product identity comes from the email text and the URL is rediscovered.
"""

from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from html import unescape
from urllib.parse import urlparse

from imap_tools import AND, MailBox, MailMessageFlags

from baml_client.sync_client import b
from baml_client.types import NewsletterProduct, SearchCandidate
from pipeline.sources.utils import tavily_search
from pipeline.utils import log

IMAP_PORT_DEFAULT = 993
IMAP_FOLDER = "sub"
RESOLVE_CONCURRENCY = 5

# sender -> display name. "@x" matches any address ending in x; otherwise exact match.
# Senders with a working RSS feed have moved to pipeline/sources/rss.py (or, for
# Ben's Bites, are already covered by substack-sources.json) - IMAP stays as the
# fallback for newsletters that don't publish one.
NEWSLETTER_SOURCES: list[tuple[str, str]] = [
    ("@deeperlearning.producthunt.com", "The Frontier by Product Hunt"),
    ("@changelog.com", "Changelog News"),
    ("@deeplearning.ai", "The Batch"),
    ("@pointer.io", "Pointer"),
    ("@mail.theresanaiforthat.com", "There's An AI For That"),
    ("@technews.therundown.ai", "The Rundown AI Tech"),
    ("@mail.joinsuperhuman.ai", "Superhuman"),
    ("agentai@mail.beehiiv.com", "AgentAI"),
]

# Never a product's first-party source: social posts, video, aggregators/content farms.
DENY_DOMAINS = [
    "x.com",
    "twitter.com",
    "t.co",
    "linkedin.com",
    "reddit.com",
    "threads.net",
    "mastodon.social",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "digg.com",
    "medium.com",
    "news.ycombinator.com",
]

_STYLE_RE = re.compile(r"<style[^>]*>[\s\S]*?</style>", re.IGNORECASE)
_SCRIPT_RE = re.compile(r"<script[^>]*>[\s\S]*?</script>", re.IGNORECASE)
_ANCHOR_RE = re.compile(r'<a[^>]*href="([^"]*)"[^>]*>([\s\S]*?)</a>', re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _match_sender(address: str) -> str | None:
    addr = address.lower()
    for pattern, name in NEWSLETTER_SOURCES:
        p = pattern.lower()
        if addr.endswith(p) if p.startswith("@") else addr == p:
            return name
    return None


def _html_to_text(html: str) -> str:
    """Strip an email's HTML to text, keeping anchor text with hrefs as a weak
    hint. Hrefs are usually tracking redirects, so product identity comes from
    the surrounding words, not the link.
    """
    cleaned = _STYLE_RE.sub("", html)
    cleaned = _SCRIPT_RE.sub("", cleaned)

    def _anchor(m: re.Match[str]) -> str:
        text = _TAG_RE.sub("", m.group(2)).strip()
        return f"[{text}]({m.group(1)})" if text else ""

    cleaned = _ANCHOR_RE.sub(_anchor, cleaned)
    cleaned = _TAG_RE.sub(" ", cleaned)
    cleaned = unescape(cleaned)
    cleaned = _WS_RE.sub(" ", cleaned).strip()
    return cleaned[:50_000]


def _extract_products(html: str, newsletter_name: str, email_date: str) -> list[dict]:
    text = _html_to_text(html)
    if not text:
        return []
    try:
        products = b.ExtractProducts(text)
    except Exception as e:
        log(f"  Failed to extract products from {newsletter_name}: {e}")
        return []
    return [
        {
            "name": p.name.strip(),
            "description": (p.description or "").strip(),
            "email_date": email_date,
            "newsletter_name": newsletter_name,
        }
        for p in products
        if p.name and p.name.strip()
    ]


def _is_denied(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").removeprefix("www.").lower()
    except Exception:
        return True
    if not host:
        return True
    return any(host == d or host.endswith(f".{d}") for d in DENY_DOMAINS)


def _resolve_one(product: dict) -> dict | None:
    """One product -> one canonical URL, or None if nothing is a clean first-party source."""
    name = product["name"]
    description = product["description"]
    query = f"{name} {description}".strip()

    try:
        results = tavily_search(query)
    except Exception as e:
        log(f'    Search failed for "{name}": {e}')
        return None

    results = [r for r in results if not _is_denied(r["url"])]
    if not results:
        log(f'    No usable search result for "{name}"')
        return None

    try:
        choice = b.SelectProductLink(
            name,
            description,
            [
                SearchCandidate(title=r["title"], url=r["url"], snippet=r["description"])
                for r in results
            ],
        )
    except Exception as e:
        log(f'    Link selection failed for "{name}": {e}')
        return None

    # index is 1-based; 0 means "no candidate is a clean first-party source".
    picked = results[choice.index - 1] if choice.index >= 1 else None
    if not picked:
        log(f'    Dropped "{name}": no first-party result among candidates')
        return None

    return {
        "title": name,
        "url": picked["url"],
        "content": description,
        "published_date": product["email_date"],
        "source": product["newsletter_name"],
        "source_type": "newsletter",
    }


def _resolve_products(raw: list[dict]) -> list[dict]:
    """Dedupe products by name across all issues in this run, drop the
    un-notable ones, then resolve each survivor to a URL.
    """
    if not raw:
        return []

    by_name: dict[str, dict] = {}
    for p in raw:
        by_name.setdefault(p["name"].lower(), p)
    unique = list(by_name.values())

    products = unique
    try:
        keep = b.SelectNotableProducts(
            [NewsletterProduct(name=p["name"], description=p["description"]) for p in unique]
        )
        keep_idx = set(keep)
        selected = [p for i, p in enumerate(unique) if (i + 1) in keep_idx]
        if selected:  # guard against a degenerate empty response dropping everything
            products = selected
    except Exception as e:
        log(f"  Notability filter failed, resolving all: {e}")

    log(
        f"  Resolving {len(products)} notable products via search "
        f"({len(raw)} raw -> {len(unique)} unique -> {len(products)} notable)"
    )

    articles: list[dict] = []
    with ThreadPoolExecutor(max_workers=RESOLVE_CONCURRENCY) as ex:
        futures = [ex.submit(_resolve_one, p) for p in products]
        for f in as_completed(futures):
            article = f.result()
            if article:
                articles.append(article)

    log(f"  Resolved {len(articles)}/{len(products)} products to URLs")
    return articles


def _imap_config() -> dict:
    host = os.environ.get("IMAP_HOST")
    user = os.environ.get("IMAP_USER")
    password = os.environ.get("IMAP_PASSWORD")
    if not host or not user or not password:
        raise RuntimeError("Missing IMAP env vars: IMAP_HOST, IMAP_USER, IMAP_PASSWORD")
    port = int(os.environ.get("IMAP_PORT", IMAP_PORT_DEFAULT))
    return {"host": host, "port": port, "user": user, "password": password}


def _run_imap_fetch(config: dict) -> list[dict]:
    """One connect -> fetch -> mark-seen -> logout cycle. Two passes: headers
    only to find matches (avoids downloading full bodies of unrelated mail),
    then full source for matched UIDs only.
    """
    raw: list[dict] = []

    with MailBox(config["host"], port=config["port"]).login(
        config["user"], config["password"], initial_folder=IMAP_FOLDER
    ) as mb:
        matches: dict[str, str] = {}
        for msg in mb.fetch(AND(seen=False), mark_seen=False, headers_only=True):
            name = _match_sender(msg.from_ or "")
            if name:
                matches[msg.uid] = name

        log(f"  Found {len(matches)} unread newsletter emails")
        if not matches:
            return raw

        processed_uids: list[str] = []
        for msg in mb.fetch(
            AND(uid=",".join(matches.keys())), mark_seen=False, headers_only=False
        ):
            name = matches.get(msg.uid)
            if not name:
                continue

            subject = msg.subject or "(no subject)"
            log(f"  Processing: {name} ({subject})")

            html = msg.html or msg.text or ""
            if not html:
                log("    No HTML content, skipping")
                processed_uids.append(msg.uid)
                continue

            email_date = (msg.date or datetime.now(UTC)).isoformat()
            products = _extract_products(html, name, email_date)
            log(f"    Found {len(products)} products")
            raw.extend(products)
            processed_uids.append(msg.uid)

        if processed_uids:
            mb.flag(processed_uids, MailMessageFlags.SEEN, True)

    return raw


def fetch_newsletter() -> list[dict]:
    if not NEWSLETTER_SOURCES:
        log("Newsletter: no sources configured, skipping")
        return []

    config = _imap_config()
    log(f"Connecting to {config['host']} as {config['user']}...")

    try:
        raw = _run_imap_fetch(config)
    except Exception as e:
        log(f"Newsletter fetch failed: {e}")
        return []

    articles = _resolve_products(raw)
    log(f"Newsletter: {len(articles)} articles extracted")
    return articles
