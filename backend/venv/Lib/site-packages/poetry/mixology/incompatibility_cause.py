from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from poetry.mixology.incompatibility import Incompatibility


class IncompatibilityCauseError(Exception):
    """
    The reason and Incompatibility's terms are incompatible.
    """


class RootCauseError(IncompatibilityCauseError):
    pass


class NoVersionsCauseError(IncompatibilityCauseError):
    pass


class DependencyCauseError(IncompatibilityCauseError):
    pass


class ConflictCauseError(IncompatibilityCauseError):
    """
    The incompatibility was derived from two existing incompatibilities
    during conflict resolution.
    """

    def __init__(self, conflict: Incompatibility, other: Incompatibility) -> None:
        self._conflict = conflict
        self._other = other

    @property
    def conflict(self) -> Incompatibility:
        return self._conflict

    @property
    def other(self) -> Incompatibility:
        return self._other

    def __str__(self) -> str:
        return str(self._conflict)


class PythonCauseError(IncompatibilityCauseError):
    """
    The incompatibility represents a package's python constraint
    (Python versions) being incompatible
    with the current python version.
    """

    def __init__(self, python_version: str, root_python_version: str) -> None:
        self._python_version = python_version
        self._root_python_version = root_python_version

    @property
    def python_version(self) -> str:
        return self._python_version

    @property
    def root_python_version(self) -> str:
        return self._root_python_version


class PlatformCauseError(IncompatibilityCauseError):
    """
    The incompatibility represents a package's platform constraint
    (OS most likely) being incompatible with the current platform.
    """

    def __init__(self, platform: str) -> None:
        self._platform = platform

    @property
    def platform(self) -> str:
        return self._platform
