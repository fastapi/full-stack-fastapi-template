from __future__ import annotations

import functools
import hashlib

from contextlib import contextmanager
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import requests
import requests.adapters

from packaging.metadata import parse_email
from poetry.core.constraints.version import parse_constraint
from poetry.core.packages.dependency import Dependency
from poetry.core.utils.helpers import temporary_directory
from poetry.core.version.markers import parse_marker

from poetry.config.config import Config
from poetry.inspection.info import PackageInfo
from poetry.inspection.lazy_wheel import LazyWheelUnsupportedError
from poetry.inspection.lazy_wheel import metadata_from_wheel_url
from poetry.repositories.cached_repository import CachedRepository
from poetry.repositories.exceptions import PackageNotFoundError
from poetry.repositories.exceptions import RepositoryError
from poetry.repositories.link_sources.html import HTMLPage
from poetry.utils.authenticator import Authenticator
from poetry.utils.constants import REQUESTS_TIMEOUT
from poetry.utils.helpers import HTTPRangeRequestSupportedError
from poetry.utils.helpers import download_file
from poetry.utils.helpers import get_highest_priority_hash_type
from poetry.utils.patterns import wheel_file_re


if TYPE_CHECKING:
    from collections.abc import Iterator

    from packaging.utils import NormalizedName
    from poetry.core.packages.utils.link import Link

    from poetry.repositories.link_sources.base import LinkSource
    from poetry.utils.authenticator import RepositoryCertificateConfig


class HTTPRepository(CachedRepository):
    def __init__(
        self,
        name: str,
        url: str,
        *,
        config: Config | None = None,
        disable_cache: bool = False,
        pool_size: int = requests.adapters.DEFAULT_POOLSIZE,
    ) -> None:
        super().__init__(name, disable_cache=disable_cache, config=config)
        self._url = url
        if config is None:
            config = Config.create()
        self._authenticator = Authenticator(
            config=config,
            cache_id=name,
            disable_cache=disable_cache,
            pool_size=pool_size,
        )
        self._authenticator.add_repository(name, url)
        self.get_page = functools.lru_cache(maxsize=None)(self._get_page)

        self._lazy_wheel = config.get("solver.lazy-wheel", True)
        self._max_retries = config.get("requests.max-retries", 0)
        # We are tracking if a domain supports range requests or not to avoid
        # unnecessary requests.
        # ATTENTION: A domain might support range requests only for some files, so the
        # meaning is as follows:
        # - Domain not in dict: We don't know anything.
        # - True: The domain supports range requests for at least some files.
        # - False: The domain does not support range requests for the files we tried.
        self._supports_range_requests: dict[str, bool] = {}

    @property
    def session(self) -> Authenticator:
        return self._authenticator

    @property
    def url(self) -> str:
        return self._url

    @property
    def certificates(self) -> RepositoryCertificateConfig:
        return self._authenticator.get_certs_for_url(self.url)

    @property
    def authenticated_url(self) -> str:
        return self._authenticator.authenticated_url(url=self.url)

    def _download(
        self, url: str, dest: Path, *, raise_accepts_ranges: bool = False
    ) -> None:
        return download_file(
            url,
            dest,
            session=self.session,
            raise_accepts_ranges=raise_accepts_ranges,
            max_retries=self._max_retries,
        )

    @contextmanager
    def _cached_or_downloaded_file(
        self, link: Link, *, raise_accepts_ranges: bool = False
    ) -> Iterator[Path]:
        self._log(f"Downloading: {link.url}", level="debug")
        with temporary_directory() as temp_dir:
            filepath = Path(temp_dir) / link.filename
            self._download(
                link.url, filepath, raise_accepts_ranges=raise_accepts_ranges
            )
            yield filepath

    def _get_info_from_wheel(self, link: Link) -> PackageInfo:
        from poetry.inspection.info import PackageInfo

        netloc = link.netloc

        # If "lazy-wheel" is enabled and the domain supports range requests
        # or we don't know yet, we try range requests.
        raise_accepts_ranges = self._lazy_wheel
        if self._lazy_wheel and self._supports_range_requests.get(netloc, True):
            try:
                package_info = PackageInfo.from_metadata(
                    metadata_from_wheel_url(link.filename, link.url, self.session)
                )
            except LazyWheelUnsupportedError as e:
                # Do not set to False if we already know that the domain supports
                # range requests for some URLs!
                self._log(
                    f"Disabling lazy wheel support for {netloc}: {e}",
                    level="debug",
                )
                raise_accepts_ranges = False
                self._supports_range_requests.setdefault(netloc, False)
            else:
                self._supports_range_requests[netloc] = True
                return package_info

        try:
            with self._cached_or_downloaded_file(
                link, raise_accepts_ranges=raise_accepts_ranges
            ) as filepath:
                return PackageInfo.from_wheel(filepath)
        except HTTPRangeRequestSupportedError:
            # The domain did not support range requests for the first URL(s) we tried,
            # but supports it for some URLs (especially the current URL),
            # so we abort the download, update _supports_range_requests to try
            # range requests for all files and use it for the current URL.
            self._log(
                f"Abort downloading {link.url} because server supports range requests",
                level="debug",
            )
            self._supports_range_requests[netloc] = True
            return self._get_info_from_wheel(link)

    def _get_info_from_sdist(self, link: Link) -> PackageInfo:
        from poetry.inspection.info import PackageInfo

        with self._cached_or_downloaded_file(link) as filepath:
            return PackageInfo.from_sdist(filepath)

    def _get_info_from_metadata(self, link: Link) -> PackageInfo | None:
        if link.has_metadata:
            try:
                assert link.metadata_url is not None
                response = self.session.get(link.metadata_url)
                if link.metadata_hashes and (
                    hash_name := get_highest_priority_hash_type(
                        link.metadata_hashes, f"{link.filename}.metadata"
                    )
                ):
                    metadata_hash = getattr(hashlib, hash_name)(
                        response.content
                    ).hexdigest()
                    if metadata_hash != link.metadata_hashes[hash_name]:
                        self._log(
                            f"Metadata file hash ({metadata_hash}) does not match"
                            f" expected hash ({link.metadata_hashes[hash_name]})."
                            f" Metadata file for {link.filename} will be ignored.",
                            level="warning",
                        )
                        return None

                metadata, _ = parse_email(response.content)
                return PackageInfo.from_metadata(metadata)

            except requests.HTTPError:
                self._log(
                    f"Failed to retrieve metadata at {link.metadata_url}",
                    level="warning",
                )

        return None

    def _get_info_from_links(
        self, links: list[Link], *, ignore_yanked: bool
    ) -> PackageInfo:
        # Sort links by distribution type
        wheels: list[Link] = []
        sdists: list[Link] = []
        for link in links:
            if link.yanked and ignore_yanked:
                # drop yanked files unless the entire release is yanked
                continue
            if link.is_wheel:
                wheels.append(link)
            elif link.filename.endswith(
                (".tar.gz", ".zip", ".bz2", ".xz", ".Z", ".tar")
            ):
                sdists.append(link)

        # Prefer to read data from wheels: this is faster and more reliable
        if wheels:
            # We ought just to be able to look at any of the available wheels to read
            # metadata, they all should give the same answer.
            #
            # In practice this hasn't always been true.
            #
            # Most of the code in here is to deal with cases such as isort 4.3.4 which
            # published separate python3 and python2 wheels with quite different
            # dependencies.  We try to detect such cases and combine the data from the
            # two wheels into what ought to have been published in the first place...
            universal_wheel = None
            universal_python2_wheel = None
            universal_python3_wheel = None
            platform_specific_wheels = []
            for wheel in wheels:
                m = wheel_file_re.match(wheel.filename)
                if not m:
                    continue

                pyver = m.group("pyver")
                abi = m.group("abi")
                plat = m.group("plat")
                if abi == "none" and plat == "any":
                    # Universal wheel
                    if pyver == "py2.py3":
                        # Any Python
                        universal_wheel = wheel
                    elif pyver == "py2":
                        universal_python2_wheel = wheel
                    else:
                        universal_python3_wheel = wheel
                else:
                    platform_specific_wheels.append(wheel)

            if universal_wheel is not None:
                return self._get_info_from_metadata(
                    universal_wheel
                ) or self._get_info_from_wheel(universal_wheel)

            info = None
            if universal_python2_wheel and universal_python3_wheel:
                info = self._get_info_from_metadata(
                    universal_python2_wheel
                ) or self._get_info_from_wheel(universal_python2_wheel)

                py3_info = self._get_info_from_metadata(
                    universal_python3_wheel
                ) or self._get_info_from_wheel(universal_python3_wheel)

                if info.requires_python or py3_info.requires_python:
                    info.requires_python = str(
                        parse_constraint(info.requires_python or "^2.7").union(
                            parse_constraint(py3_info.requires_python or "^3")
                        )
                    )

                if py3_info.requires_dist:
                    if not info.requires_dist:
                        info.requires_dist = py3_info.requires_dist

                        return info

                    py2_requires_dist = {
                        Dependency.create_from_pep_508(r).to_pep_508()
                        for r in info.requires_dist
                    }
                    py3_requires_dist = {
                        Dependency.create_from_pep_508(r).to_pep_508()
                        for r in py3_info.requires_dist
                    }
                    base_requires_dist = py2_requires_dist & py3_requires_dist
                    py2_only_requires_dist = py2_requires_dist - py3_requires_dist
                    py3_only_requires_dist = py3_requires_dist - py2_requires_dist

                    # Normalizing requires_dist
                    requires_dist = list(base_requires_dist)
                    for requirement in py2_only_requires_dist:
                        dep = Dependency.create_from_pep_508(requirement)
                        dep.marker = dep.marker.intersect(
                            parse_marker("python_version == '2.7'")
                        )
                        requires_dist.append(dep.to_pep_508())

                    for requirement in py3_only_requires_dist:
                        dep = Dependency.create_from_pep_508(requirement)
                        dep.marker = dep.marker.intersect(
                            parse_marker("python_version >= '3'")
                        )
                        requires_dist.append(dep.to_pep_508())

                    info.requires_dist = sorted(set(requires_dist))

            if info:
                return info

            # Prefer non platform specific wheels
            if universal_python3_wheel:
                return self._get_info_from_metadata(
                    universal_python3_wheel
                ) or self._get_info_from_wheel(universal_python3_wheel)

            if universal_python2_wheel:
                return self._get_info_from_metadata(
                    universal_python2_wheel
                ) or self._get_info_from_wheel(universal_python2_wheel)

            if platform_specific_wheels:
                first_wheel = platform_specific_wheels[0]
                return self._get_info_from_metadata(
                    first_wheel
                ) or self._get_info_from_wheel(first_wheel)

        return self._get_info_from_metadata(sdists[0]) or self._get_info_from_sdist(
            sdists[0]
        )

    def _links_to_data(self, links: list[Link], data: PackageInfo) -> dict[str, Any]:
        if not links:
            raise PackageNotFoundError(
                f'No valid distribution links found for package: "{data.name}" version:'
                f' "{data.version}"'
            )

        files: list[dict[str, Any]] = []
        for link in links:
            if link.yanked and not data.yanked:
                # drop yanked files unless the entire release is yanked
                continue

            file_hash: str | None
            for hash_name in ("sha512", "sha384", "sha256"):
                if hash_name in link.hashes:
                    file_hash = f"{hash_name}:{link.hashes[hash_name]}"
                    break
            else:
                file_hash = self.calculate_sha256(link)

            if file_hash is None and (
                hash_type := get_highest_priority_hash_type(link.hashes, link.filename)
            ):
                file_hash = f"{hash_type}:{link.hashes[hash_type]}"

            files.append({"file": link.filename, "hash": file_hash})

        data.files = files

        # drop yanked files unless the entire release is yanked
        info = self._get_info_from_links(links, ignore_yanked=not data.yanked)

        data.summary = info.summary
        data.requires_dist = info.requires_dist
        data.requires_python = info.requires_python

        return data.asdict()

    def calculate_sha256(self, link: Link) -> str | None:
        with self._cached_or_downloaded_file(link) as filepath:
            hash_name = get_highest_priority_hash_type(link.hashes, link.filename)
            known_hash = None
            with suppress(ValueError, AttributeError):
                # Handle ValueError here as well since under FIPS environments
                # this is what is raised (e.g., for MD5)
                known_hash = getattr(hashlib, hash_name)() if hash_name else None
            required_hash = hashlib.sha256()

            chunksize = 4096
            with filepath.open("rb") as f:
                while True:
                    chunk = f.read(chunksize)
                    if not chunk:
                        break
                    if known_hash:
                        known_hash.update(chunk)
                    required_hash.update(chunk)

            if (
                not hash_name
                or not known_hash
                or known_hash.hexdigest() == link.hashes[hash_name]
            ):
                return f"{required_hash.name}:{required_hash.hexdigest()}"
        return None

    def _get_response(self, endpoint: str) -> requests.Response | None:
        url = self._url + endpoint
        try:
            response: requests.Response = self.session.get(
                url, raise_for_status=False, timeout=REQUESTS_TIMEOUT
            )
            if response.status_code in (401, 403):
                self._log(
                    f"Authorization error accessing {url}",
                    level="warning",
                )
                return None
            if response.status_code == 404:
                return None
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RepositoryError(e)

        if response.url != url:
            self._log(
                f"Response URL {response.url} differs from request URL {url}",
                level="debug",
            )
        return response

    def _get_page(self, name: NormalizedName) -> LinkSource:
        response = self._get_response(f"/{name}/")
        if not response:
            raise PackageNotFoundError(f"Package [{name}] not found.")
        return HTMLPage(response.url, response.text)
