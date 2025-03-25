from __future__ import annotations

import logging
import operator
from typing import Callable, Iterable

from findpython.providers import ALL_PROVIDERS, BaseProvider
from findpython.python import PythonVersion
from findpython.utils import get_suffix_preference, parse_major

logger = logging.getLogger("findpython")


class Finder:
    """Find python versions on the system.

    :param resolve_symlinks: Whether to resolve symlinks.
    :param no_same_file: Whether to deduplicate with the python executable content.
    :param no_same_interpreter: Whether to deduplicate with the python executable path.
    """

    def __init__(
        self,
        resolve_symlinks: bool = False,
        no_same_file: bool = False,
        no_same_interpreter: bool = False,
        selected_providers: list[str] | None = None,
    ) -> None:
        self.resolve_symlinks = resolve_symlinks
        self.no_same_file = no_same_file
        self.no_same_interpreter = no_same_interpreter
        self._providers = self.setup_providers(selected_providers)

    def setup_providers(
        self,
        selected_providers: list[str] | None = None,
    ) -> list[BaseProvider]:
        providers: list[BaseProvider] = []
        allowed_providers = ALL_PROVIDERS
        if selected_providers is not None:
            allowed_providers = {name: ALL_PROVIDERS[name] for name in selected_providers}
        for provider_class in allowed_providers.values():
            provider = provider_class.create()
            if provider is None:
                logger.debug("Provider %s is not available", provider_class.__name__)
            else:
                providers.append(provider)
        return providers

    def add_provider(self, provider: BaseProvider, pos: int | None = None) -> None:
        """Add provider to the provider list.
        If pos is given, it will be inserted at the given position.
        """
        if pos is not None:
            self._providers.insert(pos, provider)
        else:
            self._providers.append(provider)

    def find_all(
        self,
        major: int | str | None = None,
        minor: int | None = None,
        patch: int | None = None,
        pre: bool | None = None,
        dev: bool | None = None,
        name: str | None = None,
        architecture: str | None = None,
        allow_prereleases: bool = False,
        implementation: str | None = None,
    ) -> list[PythonVersion]:
        """
        Return all Python versions matching the given version criteria.

        :param major: The major version or the version string or the name to match.
        :param minor: The minor version to match.
        :param patch: The micro version to match.
        :param pre: Whether the python is a prerelease.
        :param dev: Whether the python is a devrelease.
        :param name: The name of the python.
        :param architecture: The architecture of the python.
        :param allow_prereleases: Whether to allow prereleases.
        :param implementation: The implementation of the python. E.g. "cpython", "pypy".
        :return: a list of PythonVersion objects
        """
        if allow_prereleases and (pre is False or dev is False):
            raise ValueError(
                "If allow_prereleases is True, pre and dev must not be False."
            )
        if isinstance(major, str):
            if any(v is not None for v in (minor, patch, pre, dev, name)):
                raise ValueError(
                    "If major is a string, minor, patch, pre, dev and name "
                    "must not be specified."
                )
            version_dict = parse_major(major)
            if version_dict is not None:
                major = version_dict["major"]
                minor = version_dict["minor"]
                patch = version_dict["patch"]
                pre = version_dict["pre"]
                dev = version_dict["dev"]
                if allow_prereleases:
                    pre = pre or None
                    dev = dev or None
                architecture = version_dict["architecture"]
                implementation = version_dict["implementation"]
            else:
                name, major = major, None

        version_matcher = operator.methodcaller(
            "matches",
            major,
            minor,
            patch,
            pre,
            dev,
            name,
            architecture,
            implementation,
        )
        # Deduplicate with the python executable path
        matched_python = set(self._find_all_python_versions())
        return self._dedup(matched_python, version_matcher)

    def find(
        self,
        major: int | str | None = None,
        minor: int | None = None,
        patch: int | None = None,
        pre: bool | None = None,
        dev: bool | None = None,
        name: str | None = None,
        architecture: str | None = None,
        allow_prereleases: bool = False,
        implementation: str | None = None,
    ) -> PythonVersion | None:
        """
        Return the Python version that is closest to the given version criteria.

        :param major: The major version or the version string or the name to match.
        :param minor: The minor version to match.
        :param patch: The micro version to match.
        :param pre: Whether the python is a prerelease.
        :param dev: Whether the python is a devrelease.
        :param name: The name of the python.
        :param architecture: The architecture of the python.
        :param allow_prereleases: Whether to allow prereleases.
        :param implementation: The implementation of the python. E.g. "cpython", "pypy".
        :return: a Python object or None
        """
        return next(
            iter(
                self.find_all(
                    major,
                    minor,
                    patch,
                    pre,
                    dev,
                    name,
                    architecture,
                    allow_prereleases,
                    implementation,
                )
            ),
            None,
        )

    def _find_all_python_versions(self) -> Iterable[PythonVersion]:
        """Find all python versions on the system."""
        for provider in self._providers:
            yield from provider.find_pythons()

    def _dedup(
        self,
        python_versions: Iterable[PythonVersion],
        version_matcher: Callable[[PythonVersion], bool],
    ) -> list[PythonVersion]:
        def dedup_key(python_version: PythonVersion) -> str:
            if self.no_same_interpreter:
                return python_version.interpreter.as_posix()
            if self.no_same_file:
                return python_version.binary_hash()
            if self.resolve_symlinks and not python_version.keep_symlink:
                return python_version.real_path.as_posix()
            return python_version.executable.as_posix()

        def sort_key(python_version: PythonVersion) -> tuple[int, int, int]:
            return (
                python_version.executable.is_symlink(),
                get_suffix_preference(python_version.name),
                -len(python_version.executable.as_posix()),
            )

        result: dict[str, PythonVersion] = {}

        for python_version in sorted(python_versions, key=sort_key):
            key = dedup_key(python_version)
            if (
                key not in result
                and python_version.is_valid()
                and version_matcher(python_version)
            ):
                result[key] = python_version
        return sorted(result.values(), reverse=True)
