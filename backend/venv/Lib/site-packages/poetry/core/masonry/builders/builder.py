from __future__ import annotations

import logging
import sys
import textwrap

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from poetry.core.masonry.utils.module import Module
    from poetry.core.poetry import Poetry


METADATA_BASE = """\
Metadata-Version: 2.3
Name: {name}
Version: {version}
Summary: {summary}
"""

logger = logging.getLogger(__name__)


class Builder:
    format: str | None = None

    def __init__(
        self,
        poetry: Poetry,
        executable: Path | None = None,
        config_settings: dict[str, Any] | None = None,
    ) -> None:
        from poetry.core.masonry.metadata import Metadata

        if not poetry.is_package_mode:
            raise RuntimeError(
                "Building a package is not possible in non-package mode."
            )

        self._config_settings = config_settings or {}

        self._poetry = poetry
        self._apply_local_version_label()

        self._package = poetry.package
        self._path: Path = poetry.pyproject_path.parent
        self._excluded_files: set[str] | None = None
        self._executable = Path(executable or sys.executable)
        self._meta = Metadata.from_package(self._package)

    @cached_property
    def _module(self) -> Module:
        from poetry.core.masonry.utils.module import Module

        packages = [
            item
            for item in self._package.packages
            if not self.format or self.format in item["format"]
        ]
        includes = [
            item
            for item in self._package.include
            if not self.format or self.format in item["format"]
        ]

        return Module(
            self._package.name,
            self._path.as_posix(),
            packages=packages,
            includes=includes,
        )

    @property
    def executable(self) -> Path:
        return self._executable

    @property
    def default_target_dir(self) -> Path:
        return self._path / "dist"

    def _apply_local_version_label(self) -> None:
        """Apply local version label from config settings to the poetry package version if present."""
        if local_version_label := self._config_settings.get("local-version"):
            self._poetry.package.version = self._poetry.package.version.replace(
                local=local_version_label
            )

    def build(self, target_dir: Path | None) -> Path:
        raise NotImplementedError

    def find_excluded_files(self, fmt: str | None = None) -> set[str]:
        if self._excluded_files is None:
            from poetry.core.vcs import get_vcs

            # Checking VCS
            vcs = get_vcs(self._path)
            vcs_ignored_files = set(vcs.get_ignored_files()) if vcs else set()

            explicitly_excluded = set()
            for excluded_glob in self._package.exclude:
                for excluded in self._path.glob(str(excluded_glob)):
                    explicitly_excluded.add(
                        Path(excluded).relative_to(self._path).as_posix()
                    )

            explicitly_included = set()
            for inc in self._module.explicit_includes:
                if fmt and fmt not in inc.formats:
                    continue

                for included in inc.elements:
                    explicitly_included.add(included.relative_to(self._path).as_posix())

            ignored = (vcs_ignored_files | explicitly_excluded) - explicitly_included
            for ignored_file in ignored:
                logger.debug(f"Ignoring: {ignored_file}")

            self._excluded_files = ignored

        return self._excluded_files

    def is_excluded(self, filepath: str | Path) -> bool:
        exclude_path = Path(filepath)

        if "__pycache__" in exclude_path.parts or exclude_path.suffix == ".pyc":
            return True

        while True:
            if exclude_path.as_posix() in self.find_excluded_files(fmt=self.format):
                return True

            if len(exclude_path.parts) > 1:
                exclude_path = exclude_path.parent
            else:
                break

        return False

    def find_files_to_add(self, exclude_build: bool = True) -> set[BuildIncludeFile]:
        """
        Finds all files to add to the tarball
        """
        from poetry.core.masonry.utils.package_include import PackageInclude

        to_add = set()

        for include in self._module.includes:
            include.refresh()
            formats = include.formats

            for file in include.elements:
                if "__pycache__" in file.parts:
                    # This is just a shortcut. It will be ignored later anyway.
                    continue

                if (
                    isinstance(include, PackageInclude)
                    and include.source
                    and self.format == "wheel"
                ):
                    source_root = include.base
                else:
                    source_root = self._path

                if (
                    isinstance(include, PackageInclude)
                    and include.target
                    and self.format == "wheel"
                ):
                    target_dir = include.target
                else:
                    target_dir = None

                if file.is_dir():
                    if self.format in formats:
                        for current_file in file.glob("**/*"):
                            include_file = BuildIncludeFile(
                                path=current_file,
                                project_root=self._path,
                                source_root=source_root,
                                target_dir=target_dir,
                            )

                            if not (
                                current_file.is_dir()
                                or self.is_excluded(
                                    include_file.relative_to_project_root()
                                )
                            ):
                                to_add.add(include_file)
                    continue

                include_file = BuildIncludeFile(
                    path=file,
                    project_root=self._path,
                    source_root=source_root,
                    target_dir=target_dir,
                )

                if self.is_excluded(
                    include_file.relative_to_project_root()
                ) and isinstance(include, PackageInclude):
                    continue

                logger.debug(f"Adding: {file}")
                to_add.add(include_file)

        # add build script if it is specified and explicitly required
        if self._package.build_script and not exclude_build:
            to_add.add(
                BuildIncludeFile(
                    path=self._package.build_script,
                    project_root=self._path,
                    source_root=self._path,
                )
            )

        return to_add

    def get_metadata_content(self) -> str:
        content = METADATA_BASE.format(
            name=self._meta.name,
            version=self._meta.version,
            summary=str(self._meta.summary),
        )

        if self._meta.license:
            license_field = "License: "
            # Indentation is not only for readability, but required
            # so that the line break is not treated as end of field.
            # The exact indentation does not matter,
            # but it is essential to also indent empty lines.
            escaped_license = textwrap.indent(
                self._meta.license, " " * len(license_field), lambda line: True
            ).strip()
            content += f"{license_field}{escaped_license}\n"

        if self._meta.keywords:
            content += f"Keywords: {self._meta.keywords}\n"

        if self._meta.author:
            content += f"Author: {self._meta.author}\n"

        if self._meta.author_email:
            content += f"Author-email: {self._meta.author_email}\n"

        if self._meta.maintainer:
            content += f"Maintainer: {self._meta.maintainer}\n"

        if self._meta.maintainer_email:
            content += f"Maintainer-email: {self._meta.maintainer_email}\n"

        if self._meta.requires_python:
            content += f"Requires-Python: {self._meta.requires_python}\n"

        for classifier in self._meta.classifiers:
            content += f"Classifier: {classifier}\n"

        for extra in sorted(self._meta.provides_extra):
            content += f"Provides-Extra: {extra}\n"

        for dep in sorted(self._meta.requires_dist):
            content += f"Requires-Dist: {dep}\n"

        for url in sorted(self._meta.project_urls, key=lambda u: u[0]):
            content += f"Project-URL: {url}\n"

        if self._meta.description_content_type:
            content += (
                f"Description-Content-Type: {self._meta.description_content_type}\n"
            )

        if self._meta.description is not None:
            content += f"\n{self._meta.description}\n"

        return content

    def convert_entry_points(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}

        for group_name, group in self._poetry.package.entry_points.items():
            if group_name == "console-scripts":
                group_name = "console_scripts"
            elif group_name == "gui-scripts":
                group_name = "gui_scripts"
            result[group_name] = sorted(
                f"{name} = {specification}" for name, specification in group.items()
            )

        return result

    def convert_script_files(self) -> list[Path]:
        script_files: list[Path] = []

        for name, specification in self._poetry.local_config.get("scripts", {}).items():
            if isinstance(specification, dict) and specification.get("type") == "file":
                source = specification["reference"]

                if Path(source).is_absolute():
                    raise RuntimeError(
                        f"{source} in {name} is an absolute path. Expected relative"
                        " path."
                    )

                abs_path = Path.joinpath(self._path, source)

                if not self._package.build_script:
                    # scripts can be generated by build_script, in this case they do not exist here
                    if not abs_path.exists():
                        raise RuntimeError(
                            f"{abs_path} in script specification ({name}) is not found."
                        )
                    if not abs_path.is_file():
                        raise RuntimeError(
                            f"{abs_path} in script specification ({name}) is not a file."
                        )

                script_files.append(abs_path)

        return script_files

    def _get_legal_files(self) -> set[Path]:
        include_files_patterns = {"COPYING*", "LICEN[SC]E*", "AUTHORS*", "NOTICE*"}
        files: set[Path] = set()

        for pattern in include_files_patterns:
            files.update(self._path.glob(pattern))

        files.update(self._path.joinpath("LICENSES").glob("**/*"))
        return files


class BuildIncludeFile:
    def __init__(
        self,
        path: Path | str,
        project_root: Path | str,
        source_root: Path | str,
        target_dir: Path | str | None = None,
    ) -> None:
        """
        :param project_root: the full path of the project's root
        :param path: a full path to the file to be included
        :param source_root: the full root path to resolve to
        :param target_dir: the relative target root to resolve to
        """
        self.path = Path(path)
        self.project_root = Path(project_root).resolve()
        self.source_root = Path(source_root).resolve()
        self.target_dir = None if not target_dir else Path(target_dir)
        if not self.path.is_absolute():
            self.path = self.source_root / self.path
        else:
            self.path = self.path

        self.path = self.path.resolve()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuildIncludeFile):
            return False

        return self.path == other.path

    def __hash__(self) -> int:
        return hash(self.path)

    def __repr__(self) -> str:
        return str(self.path)

    def relative_to_project_root(self) -> Path:
        return self.path.relative_to(self.project_root)

    def relative_to_source_root(self) -> Path:
        return self.path.relative_to(self.source_root)

    def relative_to_target_root(self) -> Path:
        path = self.relative_to_source_root()
        if self.target_dir is not None:
            return self.target_dir / path
        return path
