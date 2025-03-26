from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from poetry.core.packages.dependency import Dependency


if TYPE_CHECKING:
    from collections.abc import Iterable


class URLDependency(Dependency):
    def __init__(
        self,
        name: str,
        url: str,
        *,
        directory: str | None = None,
        groups: Iterable[str] | None = None,
        optional: bool = False,
        extras: Iterable[str] | None = None,
    ) -> None:
        # Attributes must be immutable for clone() to be safe!
        # (For performance reasons, clone only creates a copy instead of a deep copy).
        self._url = url
        self._directory = directory

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"{url} does not seem like a valid url")

        super().__init__(
            name,
            "*",
            groups=groups,
            optional=optional,
            allows_prereleases=True,
            source_type="url",
            source_url=self._url,
            source_subdirectory=directory,
            extras=extras,
        )

    @property
    def url(self) -> str:
        return self._url

    @property
    def directory(self) -> str | None:
        return self._directory

    @property
    def base_pep_508_name(self) -> str:
        requirement = f"{self.complete_pretty_name} @ {self._url}"

        if self.directory:
            requirement += f"#subdirectory={self.directory}"

        return requirement

    def is_url(self) -> bool:
        return True
