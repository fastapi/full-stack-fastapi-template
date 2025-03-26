from __future__ import annotations

from contextlib import suppress
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any

import requests.adapters

from poetry.core.packages.package import Package

from poetry.inspection.info import PackageInfo
from poetry.repositories.exceptions import PackageNotFoundError
from poetry.repositories.http_repository import HTTPRepository
from poetry.repositories.link_sources.html import HTMLPage
from poetry.repositories.link_sources.html import SimpleRepositoryRootPage


if TYPE_CHECKING:
    from packaging.utils import NormalizedName
    from poetry.core.constraints.version import Version
    from poetry.core.constraints.version import VersionConstraint
    from poetry.core.packages.utils.link import Link

    from poetry.config.config import Config


class LegacyRepository(HTTPRepository):
    def __init__(
        self,
        name: str,
        url: str,
        *,
        config: Config | None = None,
        disable_cache: bool = False,
        pool_size: int = requests.adapters.DEFAULT_POOLSIZE,
    ) -> None:
        if name == "pypi":
            raise ValueError("The name [pypi] is reserved for repositories")

        super().__init__(
            name,
            url.rstrip("/"),
            config=config,
            disable_cache=disable_cache,
            pool_size=pool_size,
        )

    def package(self, name: str, version: Version) -> Package:
        """
        Retrieve the release information.

        This is a heavy task which takes time.
        We have to download a package to get the dependencies.
        We also need to download every file matching this release
        to get the various hashes.

        Note that this will be cached so the subsequent operations
        should be much faster.
        """
        try:
            index = self._packages.index(Package(name, version))

            return self._packages[index]
        except ValueError:
            package = super().package(name, version)
            package._source_type = "legacy"
            package._source_url = self._url
            package._source_reference = self.name

            return package

    def find_links_for_package(self, package: Package) -> list[Link]:
        try:
            page = self.get_page(package.name)
        except PackageNotFoundError:
            return []

        return list(page.links_for_version(package.name, package.version))

    def _find_packages(
        self, name: NormalizedName, constraint: VersionConstraint
    ) -> list[Package]:
        """
        Find packages on the remote server.
        """
        try:
            page = self.get_page(name)
        except PackageNotFoundError:
            self._log(f"No packages found for {name}", level="debug")
            return []

        versions = [
            (version, page.yanked(name, version))
            for version in page.versions(name)
            if constraint.allows(version)
        ]

        return [
            Package(
                name,
                version,
                source_type="legacy",
                source_reference=self.name,
                source_url=self._url,
                yanked=yanked,
            )
            for version, yanked in versions
        ]

    def _get_release_info(
        self, name: NormalizedName, version: Version
    ) -> dict[str, Any]:
        page = self.get_page(name)

        links = list(page.links_for_version(name, version))
        yanked = page.yanked(name, version)

        return self._links_to_data(
            links,
            PackageInfo(
                name=name,
                version=version.text,
                summary="",
                requires_dist=[],
                requires_python=None,
                files=[],
                yanked=yanked,
                cache_version=str(self.CACHE_VERSION),
            ),
        )

    def _get_page(self, name: NormalizedName) -> HTMLPage:
        if not (response := self._get_response(f"/{name}/")):
            raise PackageNotFoundError(f"Package [{name}] not found.")
        return HTMLPage(response.url, response.text)

    @cached_property
    def root_page(self) -> SimpleRepositoryRootPage:
        if not (response := self._get_response("/")):
            self._log(
                f"Unable to retrieve package listing from package source {self.name}",
                level="error",
            )
            return SimpleRepositoryRootPage()

        return SimpleRepositoryRootPage(response.text)

    def search(self, query: str | list[str]) -> list[Package]:
        results: list[Package] = []

        for candidate in self.root_page.search(query):
            with suppress(PackageNotFoundError):
                page = self.get_page(candidate)

                for package in page.packages:
                    results.append(package)

        return results
