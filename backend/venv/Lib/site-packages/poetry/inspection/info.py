from __future__ import annotations

import contextlib
import functools
import glob
import logging
import tempfile

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import pkginfo

from poetry.core.constraints.version import Version
from poetry.core.factory import Factory
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.core.utils.helpers import parse_requires
from poetry.core.utils.helpers import temporary_directory
from poetry.core.version.markers import InvalidMarkerError
from poetry.core.version.requirements import InvalidRequirementError

from poetry.utils.helpers import extractall
from poetry.utils.isolated_build import IsolatedBuildBackendError
from poetry.utils.isolated_build import isolated_builder


if TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Mapping
    from collections.abc import Sequence

    from packaging.metadata import RawMetadata
    from packaging.utils import NormalizedName
    from poetry.core.packages.project_package import ProjectPackage


logger = logging.getLogger(__name__)

DYNAMIC_METADATA_VERSION = Version.parse("2.2")


class PackageInfoError(ValueError):
    def __init__(self, path: Path, *reasons: BaseException | str) -> None:
        reasons = (f"Unable to determine package info for path: {path!s}", *reasons)
        super().__init__("\n\n".join(str(msg).strip() for msg in reasons if msg))


class PackageInfo:
    def __init__(
        self,
        *,
        name: str | None = None,
        version: str | None = None,
        summary: str | None = None,
        requires_dist: list[str] | None = None,
        requires_python: str | None = None,
        files: Sequence[Mapping[str, str]] | None = None,
        yanked: str | bool = False,
        cache_version: str | None = None,
    ) -> None:
        self.name = name
        self.version = version
        self.summary = summary
        self.requires_dist = requires_dist
        self.requires_python = requires_python
        self.files = files or []
        self.yanked = yanked
        self._cache_version = cache_version
        self._source_type: str | None = None
        self._source_url: str | None = None
        self._source_reference: str | None = None

    @property
    def cache_version(self) -> str | None:
        return self._cache_version

    def update(self, other: PackageInfo) -> PackageInfo:
        self.name = other.name or self.name
        self.version = other.version or self.version
        self.summary = other.summary or self.summary
        self.requires_dist = other.requires_dist or self.requires_dist
        self.requires_python = other.requires_python or self.requires_python
        self.files = other.files or self.files
        self._cache_version = other.cache_version or self._cache_version
        return self

    def asdict(self) -> dict[str, Any]:
        """
        Helper method to convert package info into a dictionary used for caching.
        """
        return {
            "name": self.name,
            "version": self.version,
            "summary": self.summary,
            "requires_dist": self.requires_dist,
            "requires_python": self.requires_python,
            "files": self.files,
            "yanked": self.yanked,
            "_cache_version": self._cache_version,
        }

    @classmethod
    def load(cls, data: dict[str, Any]) -> PackageInfo:
        """
        Helper method to load data from a dictionary produced by `PackageInfo.asdict()`.

        :param data: Data to load. This is expected to be a `dict` object output by
            `asdict()`.
        """
        cache_version = data.pop("_cache_version", None)
        return cls(cache_version=cache_version, **data)

    def to_package(
        self, name: str | None = None, root_dir: Path | None = None
    ) -> Package:
        """
        Create a new `poetry.core.packages.package.Package` instance using metadata from
        this instance.

        :param name: Name to use for the package, if not specified name from this
            instance is used.
        :param extras: Extras to activate for this package.
        :param root_dir:  Optional root directory to use for the package. If set,
            dependency strings will be parsed relative to this directory.
        """
        name = name or self.name

        if not name:
            raise RuntimeError("Unable to create package with no name")

        if not self.version:
            # The version could not be determined, so we raise an error since it is
            # mandatory.
            raise RuntimeError(f"Unable to retrieve the package version for {name}")

        package = Package(
            name=name,
            version=self.version,
            source_type=self._source_type,
            source_url=self._source_url,
            source_reference=self._source_reference,
            yanked=self.yanked,
        )
        if self.summary is not None:
            package.description = self.summary
        package.root_dir = root_dir
        package.python_versions = self.requires_python or "*"
        package.files = self.files

        # If this is a local poetry project, we can extract "richer" requirement
        # information, eg: development requirements etc.
        if root_dir is not None:
            path = root_dir
        elif self._source_type == "directory" and self._source_url is not None:
            path = Path(self._source_url)
        else:
            path = None

        if path is not None:
            poetry_package = self._get_poetry_package(path=path)
            if poetry_package:
                package.extras = poetry_package.extras
                for dependency in poetry_package.requires:
                    package.add_dependency(dependency)

                return package

        seen_requirements = set()

        package_extras: dict[NormalizedName, list[Dependency]] = {}
        for req in self.requires_dist or []:
            try:
                # Attempt to parse the PEP-508 requirement string
                dependency = Dependency.create_from_pep_508(req, relative_to=root_dir)
            except InvalidMarkerError:
                # Invalid marker, We strip the markers hoping for the best
                logger.warning(
                    "Stripping invalid marker (%s) found in %s-%s dependencies",
                    req,
                    package.name,
                    package.version,
                )
                req = req.split(";")[0]
                dependency = Dependency.create_from_pep_508(req, relative_to=root_dir)
            except InvalidRequirementError:
                # Unable to parse requirement so we skip it
                logger.warning(
                    "Invalid requirement (%s) found in %s-%s dependencies, skipping",
                    req,
                    package.name,
                    package.version,
                )
                continue

            if dependency.in_extras:
                # this dependency is required by an extra package
                for extra in dependency.in_extras:
                    if extra not in package_extras:
                        # this is the first time we encounter this extra for this
                        # package
                        package_extras[extra] = []

                    package_extras[extra].append(dependency)

            req = dependency.to_pep_508(with_extras=True)

            if req not in seen_requirements:
                package.add_dependency(dependency)
                seen_requirements.add(req)

        package.extras = package_extras

        return package

    @classmethod
    def _requirements_from_distribution(
        cls,
        dist: pkginfo.BDist | pkginfo.SDist | pkginfo.Wheel,
    ) -> list[str] | None:
        """
        Helper method to extract package requirements from a `pkginfo.Distribution`
        instance.

        :param dist: The distribution instance to extract requirements from.
        """
        # If the distribution lists requirements, we use those.
        #
        # If the distribution does not list requirements, but the metadata is new enough
        # to specify that this is because there definitely are none: then we return an
        # empty list.
        #
        # If there is a requires.txt, we use that.
        if dist.requires_dist:
            return list(dist.requires_dist)

        if dist.metadata_version is not None:
            metadata_version = Version.parse(dist.metadata_version)
            if (
                metadata_version >= DYNAMIC_METADATA_VERSION
                and "Requires-Dist" not in dist.dynamic
            ):
                return []

        requires = Path(dist.filename) / "requires.txt"
        if requires.exists():
            text = requires.read_text(encoding="utf-8")
            requirements = parse_requires(text)
            return requirements

        return None

    @classmethod
    def _from_distribution(
        cls, dist: pkginfo.BDist | pkginfo.SDist | pkginfo.Wheel
    ) -> PackageInfo:
        """
        Helper method to parse package information from a `pkginfo.Distribution`
        instance.

        :param dist: The distribution instance to parse information from.
        """
        # If the METADATA version is greater than the highest supported version,
        # pkginfo prints a warning and tries to parse the fields from the highest
        # known version. Assuming that METADATA versions adhere to semver,
        # this should be safe for minor updates.
        if not dist.metadata_version or dist.metadata_version.split(".")[0] not in {
            v.split(".")[0] for v in pkginfo.distribution.HEADER_ATTRS
        }:
            raise ValueError(f"Unknown metadata version: {dist.metadata_version}")

        requirements = cls._requirements_from_distribution(dist)

        info = cls(
            name=dist.name,
            version=dist.version,
            summary=dist.summary,
            requires_dist=requirements,
            requires_python=dist.requires_python,
        )

        info._source_type = "file"
        info._source_url = Path(dist.filename).resolve().as_posix()

        return info

    @classmethod
    def _from_sdist_file(cls, path: Path) -> PackageInfo:
        """
        Helper method to parse package information from an sdist file. We attempt to
        first inspect the file using `pkginfo.SDist`. If this does not provide us with
        package requirements, we extract the source and handle it as a directory.

        :param path: The sdist file to parse information from.
        """
        info = None

        with contextlib.suppress(ValueError):
            sdist = pkginfo.SDist(str(path))
            info = cls._from_distribution(sdist)

        if info is not None and info.requires_dist is not None:
            # we successfully retrieved dependencies from sdist metadata
            return info

        # Still not dependencies found
        # So, we unpack and introspect
        suffix = path.suffix
        zip = suffix == ".zip"

        if suffix == ".bz2":
            suffixes = path.suffixes
            if len(suffixes) > 1 and suffixes[-2] == ".tar":
                suffix = ".tar.bz2"
        elif not zip:
            suffix = ".tar.gz"

        with temporary_directory() as tmp_str:
            tmp = Path(tmp_str)
            extractall(source=path, dest=tmp, zip=zip)

            # a little bit of guess work to determine the directory we care about
            elements = list(tmp.glob("*"))

            if len(elements) == 1 and elements[0].is_dir():
                sdist_dir = elements[0]
            else:
                sdist_dir = tmp / path.name.rstrip(suffix)
                if not sdist_dir.is_dir():
                    sdist_dir = tmp

            # now this is an unpacked directory we know how to deal with
            new_info = cls.from_directory(path=sdist_dir)
            new_info._source_type = "file"
            new_info._source_url = path.resolve().as_posix()

        if not info:
            return new_info

        return info.update(new_info)

    @staticmethod
    def _find_dist_info(path: Path) -> Iterator[Path]:
        """
        Discover all `*.*-info` directories in a given path.

        :param path: Path to search.
        """
        pattern = "**/*.*-info"
        # Sometimes pathlib will fail on recursive symbolic links, so we need to work
        # around it and use the glob module instead. Note that this does not happen with
        # pathlib2 so it's safe to use it for Python < 3.4.
        directories = glob.iglob(path.joinpath(pattern).as_posix(), recursive=True)

        for d in directories:
            yield Path(d)

    @classmethod
    def from_metadata(cls, metadata: RawMetadata) -> PackageInfo:
        """
        Create package information from core metadata.

        :param metadata: raw metadata
        """
        return cls(
            name=metadata.get("name"),
            version=metadata.get("version"),
            summary=metadata.get("summary"),
            requires_dist=metadata.get("requires_dist"),
            requires_python=metadata.get("requires_python"),
        )

    @classmethod
    def from_metadata_directory(cls, path: Path) -> PackageInfo | None:
        """
        Helper method to parse package information from an unpacked metadata directory.

        :param path: The metadata directory to parse information from.
        """
        if path.suffix in {".dist-info", ".egg-info"}:
            directories = [path]
        else:
            directories = list(cls._find_dist_info(path=path))

        dist: pkginfo.BDist | pkginfo.SDist | pkginfo.Wheel
        for directory in directories:
            try:
                if directory.suffix == ".egg-info":
                    dist = pkginfo.UnpackedSDist(directory.as_posix())
                elif directory.suffix == ".dist-info":
                    dist = pkginfo.Wheel(directory.as_posix())
                else:
                    continue
                break
            except ValueError:
                continue
        else:
            try:
                # handle PKG-INFO in unpacked sdist root
                dist = pkginfo.UnpackedSDist(path.as_posix())
            except ValueError:
                return None

        return cls._from_distribution(dist=dist)

    @classmethod
    def from_package(cls, package: Package) -> PackageInfo:
        """
        Helper method to inspect a `Package` object, in order to generate package info.

        :param package: This must be a poetry package instance.
        """
        requires = {dependency.to_pep_508() for dependency in package.requires}

        for extra_requires in package.extras.values():
            for dependency in extra_requires:
                requires.add(dependency.to_pep_508())

        return cls(
            name=package.name,
            version=str(package.version),
            summary=package.description,
            requires_dist=list(requires),
            requires_python=package.python_versions,
            files=package.files,
            yanked=package.yanked_reason if package.yanked else False,
        )

    @staticmethod
    def _get_poetry_package(path: Path) -> ProjectPackage | None:
        # Note: we ignore any setup.py file at this step
        # TODO: add support for handling non-poetry PEP-517 builds
        if PyProjectTOML(path.joinpath("pyproject.toml")).is_poetry_project():
            with contextlib.suppress(RuntimeError):
                return Factory().create_poetry(path).package

        return None

    @classmethod
    def from_directory(cls, path: Path) -> PackageInfo:
        """
        Generate package information from a package source directory. If introspection
        of all available metadata fails, the package is attempted to be built in an
        isolated environment so as to generate required metadata.

        :param path: Path to generate package information from.
        """
        project_package = cls._get_poetry_package(path)
        info: PackageInfo | None
        if project_package:
            info = cls.from_package(project_package)
        else:
            info = cls.from_metadata_directory(path)

            if not info or info.requires_dist is None:
                try:
                    info = get_pep517_metadata(path)
                except PackageInfoError:
                    if not info:
                        raise

                    # we discovered PkgInfo but no requirements were listed

        info._source_type = "directory"
        info._source_url = path.as_posix()

        return info

    @classmethod
    def from_sdist(cls, path: Path) -> PackageInfo:
        """
        Gather package information from an sdist file, packed or unpacked.

        :param path: Path to an sdist file or unpacked directory.
        """
        if path.is_file():
            return cls._from_sdist_file(path=path)

        # if we get here then it is neither an sdist instance nor a file
        # so, we assume this is an directory
        return cls.from_directory(path=path)

    @classmethod
    def from_wheel(cls, path: Path) -> PackageInfo:
        """
        Gather package information from a wheel.

        :param path: Path to wheel.
        """
        try:
            wheel = pkginfo.Wheel(str(path))
            return cls._from_distribution(wheel)
        except ValueError as e:
            raise PackageInfoError(path, e)

    @classmethod
    def from_bdist(cls, path: Path) -> PackageInfo:
        """
        Gather package information from a bdist (wheel etc.).

        :param path: Path to bdist.
        """
        if path.suffix == ".whl":
            return cls.from_wheel(path=path)

        try:
            bdist = pkginfo.BDist(str(path))
            return cls._from_distribution(bdist)
        except ValueError as e:
            raise PackageInfoError(path, e)

    @classmethod
    def from_path(cls, path: Path) -> PackageInfo:
        """
        Gather package information from a given path (bdist, sdist, directory).

        :param path: Path to inspect.
        """
        try:
            return cls.from_bdist(path=path)
        except PackageInfoError:
            return cls.from_sdist(path=path)


@functools.cache
def get_pep517_metadata(path: Path) -> PackageInfo:
    """
    Helper method to use PEP-517 library to build and read package metadata.

    :param path: Path to package source to build and read metadata for.
    """
    info = None

    with tempfile.TemporaryDirectory() as dist:
        try:
            dest = Path(dist)

            with isolated_builder(path, "wheel") as builder:
                builder.metadata_path(dest)

            info = PackageInfo.from_metadata_directory(dest)
        except IsolatedBuildBackendError as e:
            raise PackageInfoError(path, str(e)) from None

    if info:
        return info

    # if we reach here, everything has failed and all hope is lost
    raise PackageInfoError(path, "Exhausted all core metadata sources.")
