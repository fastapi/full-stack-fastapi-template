from __future__ import annotations

from html.parser import HTMLParser


class HTMLPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.base_url: str | None = None
        self.anchors: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "base" and self.base_url is None:
            base_url = dict(attrs).get("href")
            if base_url is not None:
                self.base_url = base_url
        elif tag == "a":
            self.anchors.append(dict(attrs))
