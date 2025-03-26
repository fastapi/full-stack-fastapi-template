from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.repositories import Repository


if TYPE_CHECKING:
    from poetry.core.packages.package import Package


class LockfileRepository(Repository):
    """
    Special repository that distinguishes packages not only by name and version,
    but also by source type, url, etc.
    """

    def __init__(self) -> None:
        super().__init__("poetry-lockfile")

    def has_package(self, package: Package) -> bool:
        return any(p == package for p in self.packages)
