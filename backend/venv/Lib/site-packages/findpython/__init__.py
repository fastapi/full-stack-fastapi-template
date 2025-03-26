"""
    FindPython
    ~~~~~~~~~~
    A utility to find python versions on your system
"""
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from findpython.finder import Finder
from findpython.providers import ALL_PROVIDERS
from findpython.providers.base import BaseProvider
from findpython.python import PythonVersion


def find(*args, **kwargs) -> PythonVersion | None:
    """
    Return the Python version that is closest to the given version criteria.

    :param major: The major version or the version string or the name to match.
    :param minor: The minor version to match.
    :param patch: The micro version to match.
    :param pre: Whether the python is a prerelease.
    :param dev: Whether the python is a devrelease.
    :param name: The name of the python.
    :param architecture: The architecture of the python.
    :return: a Python object or None
    """
    return Finder().find(*args, **kwargs)


def find_all(*args, **kwargs) -> list[PythonVersion]:
    """
    Return all Python versions matching the given version criteria.

    :param major: The major version or the version string or the name to match.
    :param minor: The minor version to match.
    :param patch: The micro version to match.
    :param pre: Whether the python is a prerelease.
    :param dev: Whether the python is a devrelease.
    :param name: The name of the python.
    :param architecture: The architecture of the python.
    :return: a list of PythonVersion objects
    """
    return Finder().find_all(*args, **kwargs)


if TYPE_CHECKING:
    P = TypeVar("P", bound=type[BaseProvider])


def register_provider(provider: P) -> P:
    """
    Register a provider to use when finding python versions.

    :param provider: A provider class
    """
    ALL_PROVIDERS[provider.name()] = provider
    return provider


__all__ = ["Finder", "find", "find_all", "PythonVersion", "register_provider"]
