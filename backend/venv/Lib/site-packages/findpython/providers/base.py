from __future__ import annotations

import abc
import logging
import typing as t
from pathlib import Path

from findpython.python import PythonVersion
from findpython.utils import path_is_python, safe_iter_dir

logger = logging.getLogger("findpython")


class BaseProvider(metaclass=abc.ABCMeta):
    """The base class for python providers"""

    version_maker: t.Callable[..., PythonVersion] = PythonVersion

    @classmethod
    def name(cls) -> str:
        """Configuration name for this provider.

        By default, the lowercase class name with 'provider' removed.
        """
        self_name = cls.__name__.lower()
        if self_name.endswith("provider"):
            self_name = self_name[: -len("provider")]
        return self_name

    @classmethod
    @abc.abstractmethod
    def create(cls) -> t.Self | None:
        """Return an instance of the provider or None if it is not available"""
        pass

    @abc.abstractmethod
    def find_pythons(self) -> t.Iterable[PythonVersion]:
        """Return the python versions found by the provider"""
        pass

    @classmethod
    def find_pythons_from_path(
        cls, path: Path, as_interpreter: bool = False
    ) -> t.Iterable[PythonVersion]:
        """A general helper method to return pythons under a given path.

        :param path: The path to search for pythons
        :param as_interpreter: Use the path as the interpreter path.
            If the pythons might be a wrapper script, don't set this to True.
        :returns: An iterable of PythonVersion objects
        """
        return (
            cls.version_maker(
                child.absolute(),
                _interpreter=child.absolute() if as_interpreter else None,
            )
            for child in safe_iter_dir(path)
            if path_is_python(child)
        )
