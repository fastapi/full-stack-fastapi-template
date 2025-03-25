from __future__ import annotations

import contextlib
import logging

from typing import TYPE_CHECKING
from typing import Any

import requests
import requests.adapters

from cachecontrol.controller import logger as cache_control_logger
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.core.packages.utils.link import Link
from poetry.core.version.exceptions import InvalidVersionError
from poetry.core.version.requirements import InvalidRequirementError

from poetry.repositories.exceptions import PackageNotFoundError
from poetry.repositories.http_repository import HTTPRepository
from poetry.repositories.link_sources.json import SimpleJsonPage
from poetry.repositories.parsers.pypi_search_parser import SearchResultParser
from poetry.utils.constants import REQUESTS_TIMEOUT


cache_control_logger.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from packaging.utils import NormalizedName
    from poetry.core.constraints.version import Version
    from poetry.core.constraints.version import VersionConstraint

    from poetry.config.config import Config

SUPPORTED_PACKAGE_TYPES = {"sdist", "bdist_wheel"}


class PyPiRepository(HTTPRepository):
    def __init__(
        self,
        url: str = "https://pypi.org/",
        *,
        config: Config | None = None,
        disable_cache: bool = False,
        pool_size: int = requests.adapters.DEFAULT_POOLSIZE,
        fallback: bool = True,
    ) -> None:
        super().__init__(
            "PyPI",
            url.rstrip("/") + "/simple/",
            config=config,
            disable_cache=disable_cache,
            pool_size=pool_size,
        )

        self._base_url = url
        self._fallback = fallback

    def search(self, query: str | list[str]) -> list[Package]:
        results = []

        response = requests.get(
            self._base_url + "search", params={"q": query}, timeout=REQUESTS_TIMEOUT
        )
        parser = SearchResultParser()
        parser.feed(response.text)

        for result in parser.results:
            try:
                package = Package(result.name, result.version)
                package.description = result.description.strip()
                results.append(package)
            except InvalidVersionError:
                self._log(
                    f'Unable to parse version "{result.version}" for the'
                    f" {result.name} package, skipping",
                    level="debug",
                )

        if not results:
            # in cases like PyPI search might not be available, we fallback to explicit searches
            # to allow for a nicer ux rather than finding nothing at all
            # see: https://discuss.python.org/t/fastly-interfering-with-pypi-search/73597/6
            #
            tokens = query if isinstance(query, list) else [query]
            for token in tokens:
                with contextlib.suppress(InvalidRequirementError):
                    results.extend(
                        self.find_packages(Dependency.create_from_pep_508(token))
                    )

        return results

    def get_package_info(self, name: NormalizedName) -> dict[str, Any]:
        """
        Return the package information given its name.

        The information is returned from the cache if it exists
        or retrieved from the remote server.
        """
        return self._get_package_info(name)

    def _find_packages(
        self, name: NormalizedName, constraint: VersionConstraint
    ) -> list[Package]:
        """
        Find packages on the remote server.
        """
        try:
            json_page = self.get_page(name)
        except PackageNotFoundError:
            self._log(f"No packages found for {name}", level="debug")
            return []

        versions = [
            (version, json_page.yanked(name, version))
            for version in json_page.versions(name)
            if constraint.allows(version)
        ]

        return [Package(name, version, yanked=yanked) for version, yanked in versions]

    def _get_package_info(self, name: NormalizedName) -> dict[str, Any]:
        headers = {"Accept": "application/vnd.pypi.simple.v1+json"}
        info = self._get(f"simple/{name}/", headers=headers)
        if info is None:
            raise PackageNotFoundError(f"Package [{name}] not found.")

        return info

    def find_links_for_package(self, package: Package) -> list[Link]:
        json_data = self._get(f"pypi/{package.name}/{package.version}/json")
        if json_data is None:
            return []

        links = []
        for url in json_data["urls"]:
            if url["packagetype"] in SUPPORTED_PACKAGE_TYPES:
                h = f"sha256={url['digests']['sha256']}"
                links.append(Link(url["url"] + "#" + h, yanked=self._get_yanked(url)))

        return links

    def _get_release_info(
        self, name: NormalizedName, version: Version
    ) -> dict[str, Any]:
        from poetry.inspection.info import PackageInfo

        self._log(f"Getting info for {name} ({version}) from PyPI", "debug")

        json_data = self._get(f"pypi/{name}/{version}/json")
        if json_data is None:
            raise PackageNotFoundError(f"Package [{name}] not found.")

        info = json_data["info"]

        data = PackageInfo(
            name=info["name"],
            version=info["version"],
            summary=info["summary"],
            requires_dist=info["requires_dist"],
            requires_python=info["requires_python"],
            yanked=self._get_yanked(info),
            cache_version=str(self.CACHE_VERSION),
        )

        try:
            version_info = json_data["urls"]
        except KeyError:
            version_info = []

        files = info.get("files", [])
        for file_info in version_info:
            if file_info["packagetype"] in SUPPORTED_PACKAGE_TYPES:
                files.append(
                    {
                        "file": file_info["filename"],
                        "hash": "sha256:" + file_info["digests"]["sha256"],
                    }
                )
        data.files = files

        if self._fallback and data.requires_dist is None:
            self._log(
                "No dependencies found, downloading metadata and/or archives",
                level="debug",
            )
            # No dependencies set (along with other information)
            # This might be due to actually no dependencies
            # or badly set metadata when uploading.
            # So, we need to make sure there is actually no
            # dependencies by introspecting packages.
            page = self.get_page(name)
            links = list(page.links_for_version(name, version))
            info = self._get_info_from_links(links, ignore_yanked=not data.yanked)

            data.requires_dist = info.requires_dist

            if not data.requires_python:
                data.requires_python = info.requires_python

        return data.asdict()

    def _get_page(self, name: NormalizedName) -> SimpleJsonPage:
        source = self._base_url + f"simple/{name}/"
        info = self.get_package_info(name)
        return SimpleJsonPage(source, info)

    def _get(
        self, endpoint: str, headers: dict[str, str] | None = None
    ) -> dict[str, Any] | None:
        try:
            json_response = self.session.get(
                self._base_url + endpoint,
                raise_for_status=False,
                timeout=REQUESTS_TIMEOUT,
                headers=headers,
            )
        except requests.exceptions.TooManyRedirects:
            # Cache control redirect loop.
            # We try to remove the cache and try again
            self.session.delete_cache(self._base_url + endpoint)
            json_response = self.session.get(
                self._base_url + endpoint,
                raise_for_status=False,
                timeout=REQUESTS_TIMEOUT,
                headers=headers,
            )

        if json_response.status_code != 200:
            return None

        json: dict[str, Any] = json_response.json()
        return json

    @staticmethod
    def _get_yanked(json_data: dict[str, Any]) -> str | bool:
        if json_data.get("yanked", False):
            return json_data.get("yanked_reason") or True
        return False
