from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any

from poetry.core.packages.utils.link import Link

from poetry.repositories.link_sources.base import LinkSource


if TYPE_CHECKING:
    from poetry.repositories.link_sources.base import LinkCache


class SimpleJsonPage(LinkSource):
    """Links as returned by PEP 691 compatible JSON-based Simple API."""

    def __init__(self, url: str, content: dict[str, Any]) -> None:
        super().__init__(url=url)
        self.content = content

    @cached_property
    def _link_cache(self) -> LinkCache:
        links: LinkCache = defaultdict(lambda: defaultdict(list))
        for file in self.content["files"]:
            url = file["url"]
            requires_python = file.get("requires-python")
            yanked = file.get("yanked", False)

            # see https://peps.python.org/pep-0714/#clients
            # and https://peps.python.org/pep-0691/#project-detail
            metadata: dict[str, str] | bool = False
            for metadata_key in ("core-metadata", "dist-info-metadata"):
                if metadata_key in file:
                    metadata_value = file[metadata_key]
                    if metadata_value and isinstance(metadata_value, dict):
                        metadata = metadata_value
                    else:
                        metadata = bool(metadata_value)
                    break

            link = Link(
                url, requires_python=requires_python, yanked=yanked, metadata=metadata
            )

            if link.ext not in self.SUPPORTED_FORMATS:
                continue

            pkg = self.link_package_data(link)
            if pkg:
                links[pkg.name][pkg.version].append(link)

        return links
