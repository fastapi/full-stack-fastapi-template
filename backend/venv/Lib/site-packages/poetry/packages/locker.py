from __future__ import annotations

import json
import logging
import os
import re
import warnings

from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import cast

from packaging.utils import canonicalize_name
from poetry.core.constraints.version import Version
from poetry.core.constraints.version import parse_constraint
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.core.version.markers import parse_marker
from poetry.core.version.requirements import InvalidRequirementError
from tomlkit import array
from tomlkit import comment
from tomlkit import document
from tomlkit import inline_table
from tomlkit import table

from poetry.__version__ import __version__
from poetry.packages.transitive_package_info import TransitivePackageInfo
from poetry.toml.file import TOMLFile
from poetry.utils._compat import tomllib


if TYPE_CHECKING:
    from packaging.utils import NormalizedName
    from poetry.core.packages.directory_dependency import DirectoryDependency
    from poetry.core.packages.file_dependency import FileDependency
    from poetry.core.packages.url_dependency import URLDependency
    from poetry.core.packages.vcs_dependency import VCSDependency
    from tomlkit.toml_document import TOMLDocument

    from poetry.repositories.lockfile_repository import LockfileRepository

logger = logging.getLogger(__name__)
_GENERATED_IDENTIFIER = "@" + "generated"
GENERATED_COMMENT = (
    f"This file is automatically {_GENERATED_IDENTIFIER} by Poetry"
    f" {__version__} and should not be changed by hand."
)


class Locker:
    _VERSION = "2.1"
    _READ_VERSION_RANGE = ">=1,<3"

    _legacy_keys: ClassVar[list[str]] = [
        "dependencies",
        "source",
        "extras",
        "dev-dependencies",
    ]
    _relevant_keys: ClassVar[list[str]] = [*_legacy_keys, "group"]
    _relevant_project_keys: ClassVar[list[str]] = [
        "requires-python",
        "dependencies",
        "optional-dependencies",
    ]

    def __init__(self, lock: Path, pyproject_data: dict[str, Any]) -> None:
        self._lock = lock
        self._pyproject_data = pyproject_data
        self._lock_data: dict[str, Any] | None = None
        self._content_hash = self._get_content_hash()

    @property
    def lock(self) -> Path:
        return self._lock

    @property
    def lock_data(self) -> dict[str, Any]:
        if self._lock_data is None:
            self._lock_data = self._get_lock_data()

        return self._lock_data

    def is_locked(self) -> bool:
        """
        Checks whether the locker has been locked (lockfile found).
        """
        return self._lock.exists()

    def is_fresh(self) -> bool:
        """
        Checks whether the lock file is still up to date with the current hash.
        """
        with self.lock.open("rb") as f:
            lock = tomllib.load(f)
        metadata = lock.get("metadata", {})

        if "content-hash" in metadata:
            fresh: bool = self._content_hash == metadata["content-hash"]
            return fresh

        return False

    def is_locked_groups_and_markers(self) -> bool:
        if not self.is_locked():
            return False

        version = Version.parse(self.lock_data["metadata"]["lock-version"])
        return version >= Version.parse("2.1")

    def set_pyproject_data(self, pyproject_data: dict[str, Any]) -> None:
        self._pyproject_data = pyproject_data
        self._content_hash = self._get_content_hash()

    def set_local_config(self, local_config: dict[str, Any]) -> None:
        warnings.warn(
            "Locker.set_local_config() is deprecated and will be removed in a future"
            " release. Use Locker.set_pyproject_data() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._pyproject_data.setdefault("tool", {})["poetry"] = local_config
        self._content_hash = self._get_content_hash()

    def locked_repository(self) -> LockfileRepository:
        """
        Searches and returns a repository of locked packages.
        """
        from poetry.repositories.lockfile_repository import LockfileRepository

        repository = LockfileRepository()

        if not self.is_locked():
            return repository

        locked_packages = cast("list[dict[str, Any]]", self.lock_data["package"])

        if not locked_packages:
            return repository

        for info in locked_packages:
            repository.add_package(self._get_locked_package(info))

        return repository

    def locked_packages(self) -> dict[Package, TransitivePackageInfo]:
        if not self.is_locked_groups_and_markers():
            raise RuntimeError(
                "This method should not be called if the lock file"
                " is not at least version 2.1."
            )

        locked_packages: dict[Package, TransitivePackageInfo] = {}

        locked_package_info = cast("list[dict[str, Any]]", self.lock_data["package"])

        for info in locked_package_info:
            package = self._get_locked_package(info, with_dependencies=False)
            groups = set(info["groups"])
            locked_marker = info.get("markers", "*")
            if isinstance(locked_marker, str):
                markers = {group: parse_marker(locked_marker) for group in groups}
            else:
                markers = {
                    group: parse_marker(locked_marker.get(group, "*"))
                    for group in groups
                }
            locked_packages[package] = TransitivePackageInfo(0, groups, markers)

        return locked_packages

    def set_lock_data(
        self, root: Package, packages: dict[Package, TransitivePackageInfo]
    ) -> bool:
        """Store lock data and eventually persist to the lock file"""
        lock = self._compute_lock_data(root, packages)

        if self._should_write(lock):
            self._write_lock_data(lock)
            return True

        return False

    def _compute_lock_data(
        self, root: Package, packages: dict[Package, TransitivePackageInfo]
    ) -> TOMLDocument:
        package_specs = self._lock_packages(packages)
        # Retrieving hashes
        for package in package_specs:
            files = array()

            for f in package["files"]:
                file_metadata = inline_table()
                for k, v in sorted(f.items()):
                    file_metadata[k] = v

                files.append(file_metadata)

            package["files"] = files.multiline(True)

        lock = document()
        lock.add(comment(GENERATED_COMMENT))
        lock["package"] = package_specs

        if root.extras:
            lock["extras"] = {
                extra: sorted(dep.pretty_name for dep in deps)
                for extra, deps in sorted(root.extras.items())
            }

        lock["metadata"] = {
            "lock-version": self._VERSION,
            "python-versions": root.python_versions,
            "content-hash": self._content_hash,
        }

        return lock

    def _should_write(self, lock: TOMLDocument) -> bool:
        # if lock file exists: compare with existing lock data
        do_write = True
        if self.is_locked():
            try:
                lock_data = self.lock_data
            except RuntimeError:
                # incompatible, invalid or no lock file
                pass
            else:
                do_write = lock != lock_data
        return do_write

    def _write_lock_data(self, data: TOMLDocument) -> None:
        if self.lock.exists():
            # The following code is roughly equivalent to
            # • lockfile = TOMLFile(self.lock)
            # • lockfile.read()
            # • lockfile.write(data)
            # However, lockfile.read() takes more than half a second even
            # for a modestly sized project like Poetry itself and the only reason
            # for reading the lockfile is to determine the line endings. Thus,
            # we do that part for ourselves here, which only takes about 10 ms.

            # get original line endings
            with open(self.lock, encoding="utf-8", newline="") as f:
                line = f.readline()
            linesep = "\r\n" if line.endswith("\r\n") else "\n"

            # enforce original line endings
            content = data.as_string()
            if linesep == "\n":
                content = content.replace("\r\n", "\n")
            elif linesep == "\r\n":
                content = re.sub(r"(?<!\r)\n", "\r\n", content)
            with open(self.lock, "w", encoding="utf-8", newline="") as f:
                f.write(content)

        else:
            lockfile = TOMLFile(self.lock)
            lockfile.write(data)

        self._lock_data = None

    def _get_content_hash(self) -> str:
        """
        Returns the sha256 hash of the sorted content of the pyproject file.
        """
        project_content = self._pyproject_data.get("project", {})
        tool_poetry_content = self._pyproject_data.get("tool", {}).get("poetry", {})

        relevant_project_content = {}
        for key in self._relevant_project_keys:
            data = project_content.get(key)
            if data is not None:
                relevant_project_content[key] = data

        relevant_poetry_content = {}
        for key in self._relevant_keys:
            data = tool_poetry_content.get(key)

            if data is None and (
                # Special handling for legacy keys is just for backwards compatibility,
                # and thereby not required if there is relevant content in [project].
                key not in self._legacy_keys or relevant_project_content
            ):
                continue

            relevant_poetry_content[key] = data

        if relevant_project_content:
            relevant_content = {
                "project": relevant_project_content,
                "tool": {"poetry": relevant_poetry_content},
            }
        else:
            # For backwards compatibility, we have to put the relevant content
            # of the [tool.poetry] section at top level!
            relevant_content = relevant_poetry_content

        return sha256(json.dumps(relevant_content, sort_keys=True).encode()).hexdigest()

    def _get_lock_data(self) -> dict[str, Any]:
        if not self.lock.exists():
            raise RuntimeError("No lockfile found. Unable to read locked packages")

        with self.lock.open("rb") as f:
            try:
                lock_data = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise RuntimeError(f"Unable to read the lock file ({e}).")

        # if the lockfile doesn't contain a metadata section at all,
        # it probably needs to be rebuilt completely
        if "metadata" not in lock_data:
            raise RuntimeError(
                "The lock file does not have a metadata entry.\n"
                "Regenerate the lock file with the `poetry lock` command."
            )

        metadata = lock_data["metadata"]
        if "lock-version" not in metadata:
            raise RuntimeError(
                "The lock file is not compatible with the current version of Poetry.\n"
                "Regenerate the lock file with the `poetry lock` command."
            )
        lock_version = Version.parse(metadata["lock-version"])
        current_version = Version.parse(self._VERSION)
        accepted_versions = parse_constraint(self._READ_VERSION_RANGE)
        lock_version_allowed = accepted_versions.allows(lock_version)
        if lock_version_allowed and current_version < lock_version:
            logger.warning(
                "The lock file might not be compatible with the current version of"
                " Poetry.\nUpgrade Poetry to ensure the lock file is read properly or,"
                " alternatively, regenerate the lock file with the `poetry lock`"
                " command."
            )
        elif not lock_version_allowed:
            raise RuntimeError(
                "The lock file is not compatible with the current version of Poetry.\n"
                "Upgrade Poetry to be able to read the lock file or, alternatively, "
                "regenerate the lock file with the `poetry lock` command."
            )

        return lock_data

    def _get_locked_package(
        self, info: dict[str, Any], with_dependencies: bool = True
    ) -> Package:
        source = info.get("source", {})
        source_type = source.get("type")
        url = source.get("url")
        if source_type in ["directory", "file"]:
            url = self.lock.parent.joinpath(url).resolve().as_posix()

        name = info["name"]
        package = Package(
            name,
            info["version"],
            source_type=source_type,
            source_url=url,
            source_reference=source.get("reference"),
            source_resolved_reference=source.get("resolved_reference"),
            source_subdirectory=source.get("subdirectory"),
        )
        package.description = info.get("description", "")
        package.optional = info["optional"]
        metadata = cast("dict[str, Any]", self.lock_data["metadata"])

        # Storing of package files and hashes has been through a few generations in
        # the lockfile, we can read them all:
        #
        # - latest and preferred is that this is read per package, from
        #   package.files
        # - oldest is that hashes were stored in metadata.hashes without filenames
        # - in between those two, hashes were stored alongside filenames in
        #   metadata.files
        package_files = info.get("files")
        if package_files is not None:
            package.files = package_files
        elif "hashes" in metadata:
            hashes = cast("dict[str, Any]", metadata["hashes"])
            package.files = [{"name": h, "hash": h} for h in hashes[name]]
        elif source_type in {"git", "directory", "url"}:
            package.files = []
        else:
            files = metadata["files"][name]
            if source_type == "file":
                filename = Path(url).name
                package.files = [item for item in files if item["file"] == filename]
            else:
                # Strictly speaking, this is not correct, but we have no chance
                # to always determine which are the correct files because the
                # lockfile doesn't keep track which files belong to which package.
                package.files = files

        package.python_versions = info["python-versions"]

        if "develop" in info:
            package.develop = info["develop"]

        if with_dependencies:
            from poetry.factory import Factory

            package_extras: dict[NormalizedName, list[Dependency]] = {}
            extras = info.get("extras", {})
            if extras:
                for name, deps in extras.items():
                    name = canonicalize_name(name)
                    package_extras[name] = []

                    for dep in deps:
                        try:
                            dependency = Dependency.create_from_pep_508(dep)
                        except InvalidRequirementError:
                            # handle lock files with invalid PEP 508
                            m = re.match(r"^(.+?)(?:\[(.+?)])?(?:\s+\((.+)\))?$", dep)
                            if not m:
                                raise
                            dep_name = m.group(1)
                            extras = m.group(2) or ""
                            constraint = m.group(3) or "*"
                            dependency = Dependency(
                                dep_name, constraint, extras=extras.split(",")
                            )
                        package_extras[name].append(dependency)

            package.extras = package_extras

            for dep_name, constraint in info.get("dependencies", {}).items():
                root_dir = self.lock.parent
                if package.source_type == "directory":
                    # root dir should be the source of the package relative to the lock
                    # path
                    assert package.source_url is not None
                    root_dir = Path(package.source_url)

                if isinstance(constraint, list):
                    for c in constraint:
                        package.add_dependency(
                            Factory.create_dependency(dep_name, c, root_dir=root_dir)
                        )

                    continue

                package.add_dependency(
                    Factory.create_dependency(dep_name, constraint, root_dir=root_dir)
                )

        return package

    def _lock_packages(
        self, packages: dict[Package, TransitivePackageInfo]
    ) -> list[dict[str, Any]]:
        locked = []

        for package in sorted(
            packages,
            key=lambda x: (
                x.name,
                x.version,
                x.source_type or "",
                x.source_url or "",
                x.source_subdirectory or "",
                x.source_reference or "",
                x.source_resolved_reference or "",
            ),
        ):
            spec = self._dump_package(package, packages[package])

            locked.append(spec)

        return locked

    def _dump_package(
        self, package: Package, transitive_info: TransitivePackageInfo
    ) -> dict[str, Any]:
        dependencies: dict[str, list[Any]] = {}
        for dependency in sorted(
            package.requires,
            key=lambda d: d.name,
        ):
            dependencies.setdefault(dependency.pretty_name, [])

            constraint = inline_table()

            if dependency.is_directory():
                dependency = cast("DirectoryDependency", dependency)
                constraint["path"] = dependency.path.as_posix()

                if dependency.develop:
                    constraint["develop"] = True

            elif dependency.is_file():
                dependency = cast("FileDependency", dependency)
                constraint["path"] = dependency.path.as_posix()

            elif dependency.is_url():
                dependency = cast("URLDependency", dependency)
                constraint["url"] = dependency.url

            elif dependency.is_vcs():
                dependency = cast("VCSDependency", dependency)
                constraint[dependency.vcs] = dependency.source

                if dependency.branch:
                    constraint["branch"] = dependency.branch
                elif dependency.tag:
                    constraint["tag"] = dependency.tag
                elif dependency.rev:
                    constraint["rev"] = dependency.rev

                if dependency.directory:
                    constraint["subdirectory"] = dependency.directory

            else:
                constraint["version"] = str(dependency.pretty_constraint)

            if dependency.extras:
                constraint["extras"] = sorted(dependency.extras)

            if dependency.is_optional():
                constraint["optional"] = True

            if not dependency.marker.is_any():
                constraint["markers"] = str(dependency.marker)

            dependencies[dependency.pretty_name].append(constraint)

        # All the constraints should have the same type,
        # but we want to simplify them if it's possible
        for dependency_name, constraints in dependencies.items():
            if all(
                len(constraint) == 1 and "version" in constraint
                for constraint in constraints
            ):
                dependencies[dependency_name] = [
                    constraint["version"] for constraint in constraints
                ]

        data: dict[str, Any] = {
            "name": package.pretty_name,
            "version": package.pretty_version,
            "description": package.description or "",
            "optional": package.optional,
            "python-versions": package.python_versions,
            "groups": sorted(transitive_info.groups, key=lambda x: (x != "main", x)),
        }
        if transitive_info.markers:
            if len(markers := set(transitive_info.markers.values())) == 1:
                if not (marker := next(iter(markers))).is_any():
                    data["markers"] = str(marker)
            else:
                data["markers"] = inline_table()
                for k, v in sorted(
                    transitive_info.markers.items(),
                    key=lambda x: (x[0] != "main", x[0]),
                ):
                    if not v.is_any():
                        data["markers"][k] = str(v)
        data["files"] = sorted(package.files, key=lambda x: x["file"])

        if dependencies:
            data["dependencies"] = table()
            for k, constraints in dependencies.items():
                if len(constraints) == 1:
                    data["dependencies"][k] = constraints[0]
                else:
                    data["dependencies"][k] = array().multiline(True)
                    for constraint in constraints:
                        data["dependencies"][k].append(constraint)

        if package.extras:
            extras = {}
            for name, deps in sorted(package.extras.items()):
                extras[name] = sorted(dep.to_pep_508(with_extras=False) for dep in deps)

            data["extras"] = extras

        if package.source_url:
            url = package.source_url
            if package.source_type in ["file", "directory"]:
                # The lock file should only store paths relative to the root project
                url = Path(
                    os.path.relpath(
                        Path(url).resolve(),
                        Path(self.lock.parent).resolve(),
                    )
                ).as_posix()

            data["source"] = {}

            if package.source_type:
                data["source"]["type"] = package.source_type

            data["source"]["url"] = url

            if package.source_reference:
                data["source"]["reference"] = package.source_reference

            if package.source_resolved_reference:
                data["source"]["resolved_reference"] = package.source_resolved_reference

            if package.source_subdirectory:
                data["source"]["subdirectory"] = package.source_subdirectory

            if package.source_type in ["directory", "git"]:
                data["develop"] = package.develop

        return data
