from __future__ import annotations

import contextlib
import os
import sys

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import cast
from typing import overload

import findpython
import packaging.version

from cleo.io.null_io import NullIO
from cleo.io.outputs.output import Verbosity
from pbs_installer._install import THIS_ARCH
from pbs_installer._install import THIS_PLATFORM
from pbs_installer._versions import PYTHON_VERSIONS
from poetry.core.constraints.version import Version
from poetry.core.constraints.version import VersionConstraint
from poetry.core.constraints.version import parse_constraint

from poetry.utils.env.python.exceptions import NoCompatiblePythonVersionFoundError
from poetry.utils.env.python.providers import PoetryPythonPathProvider
from poetry.utils.env.python.providers import ShutilWhichPythonProvider


if TYPE_CHECKING:
    from collections.abc import Iterator

    from cleo.io.io import IO

    from poetry.config.config import Config
    from poetry.poetry import Poetry

# register default providers
findpython.register_provider(PoetryPythonPathProvider)


class PythonInfo(NamedTuple):
    major: int
    minor: int
    patch: int
    implementation: str
    executable: Path | None


class Python:
    @overload
    def __init__(self, *, python: findpython.PythonVersion) -> None: ...

    @overload
    def __init__(
        self, executable: str | Path, version: Version | None = None
    ) -> None: ...

    # we overload __init__ to ensure we do not break any downstream plugins
    # that use the this
    def __init__(
        self,
        executable: str | Path | None = None,
        version: Version | None = None,
        python: findpython.PythonVersion | None = None,
    ) -> None:
        if python and (executable or version):
            raise ValueError(
                "When python is provided, neither executable or version must be specified"
            )

        if python:
            self._python = python
        elif executable:
            self._python = findpython.PythonVersion(
                executable=Path(executable),
                _version=packaging.version.Version(str(version)) if version else None,
            )
        else:
            raise ValueError("Either python or executable must be provided")

    @classmethod
    def find_all(cls) -> Iterator[Python]:
        venv_path: Path | None = (
            Path(os.environ["VIRTUAL_ENV"]) if "VIRTUAL_ENV" in os.environ else None
        )
        for python in findpython.find_all():
            if venv_path and python.executable.is_relative_to(venv_path):
                continue
            yield cls(python=python)

    @classmethod
    def find_poetry_managed_pythons(cls) -> Iterator[Python]:
        finder = findpython.Finder(
            selected_providers=[PoetryPythonPathProvider.name()],
        )
        for python in finder.find_all():
            yield cls(python=python)

    @classmethod
    def find_all_versions(
        cls,
        constraint: VersionConstraint | str | None = None,
        implementation: str | None = None,
    ) -> Iterator[PythonInfo]:
        if isinstance(constraint, str):
            constraint = parse_constraint(constraint)
        constraint = constraint or parse_constraint("*")
        if implementation:
            implementation = implementation.lower()

        seen = set()
        for python in cls.find_all():
            if (
                python.executable in seen
                or not constraint.allows(python.version)
                or (implementation and python.implementation.lower() != implementation)
            ):
                continue

            seen.add(python.executable)
            yield PythonInfo(
                major=python.major,
                minor=python.minor,
                patch=python.patch,
                implementation=python.implementation.lower(),
                executable=python.executable,
            )

    @classmethod
    def find_downloadable_versions(
        cls,
        constraint: VersionConstraint | str | None = None,
        *,
        include_incompatible: bool = False,
    ) -> Iterator[PythonInfo]:
        if isinstance(constraint, str):
            constraint = parse_constraint(constraint)
        constraint = constraint or parse_constraint("*")

        for pv in PYTHON_VERSIONS:
            for _ in {
                k[1]
                for k in PYTHON_VERSIONS[pv]
                if include_incompatible or (k[0], k[1]) == (THIS_PLATFORM, THIS_ARCH)
            }:
                if not constraint.allows(
                    Version.from_parts(pv.major, pv.minor, pv.micro)
                ):
                    continue

                yield PythonInfo(
                    major=pv.major,
                    minor=pv.minor,
                    patch=pv.micro,
                    implementation=pv.implementation.lower(),
                    executable=None,
                )

    @property
    def python(self) -> findpython.PythonVersion:
        return self._python

    @property
    def name(self) -> str:
        return cast(str, self._python.name)

    @property
    def executable(self) -> Path:
        return cast(Path, self._python.interpreter)

    @property
    def implementation(self) -> str:
        return cast(str, self._python.implementation.lower())

    @property
    def major(self) -> int:
        return cast(int, self._python.major)

    @property
    def minor(self) -> int:
        return cast(int, self._python.minor)

    @property
    def patch(self) -> int:
        return cast(int, self._python.patch)

    @property
    def version(self) -> Version:
        return Version.parse(str(self._python.version))

    @cached_property
    def patch_version(self) -> Version:
        return Version.from_parts(
            major=self.version.major,
            minor=self.version.minor,
            patch=self.version.patch,
        )

    @cached_property
    def minor_version(self) -> Version:
        return Version.from_parts(major=self.version.major, minor=self.version.minor)

    @classmethod
    def get_active_python(cls) -> Python | None:
        """
        Fetches the active Python interpreter from available system paths or falls
        back to finding the first valid Python executable named "python".

        An "active Python interpreter" in this context is an executable (or a symlink)
        with the name `python`. This is done so to detect cases where pyenv or
        alternatives are used.

        This method first uses the `ShutilWhichPythonProvider` to detect Python
        executables in the path. If no interpreter is found using, it attempts
        to locate a Python binary named "python" via the `findpython` library.

        :return: An instance representing the detected active Python,
                 or None if no valid environment is found.
        """
        for python in ShutilWhichPythonProvider().find_pythons():
            return cls(python=python)

        # fallback to findpython, restrict to finding only executables
        # named "python" as the intention here is just that, nothing more
        if python := findpython.find("python"):
            return cls(python=python)

        return None

    @classmethod
    def get_system_python(cls) -> Python:
        """
        Creates and returns an instance of the class representing the Poetry's Python executable.
        """
        return cls(
            python=findpython.PythonVersion(
                executable=Path(sys.executable),
                _version=packaging.version.Version(
                    ".".join(str(v) for v in sys.version_info[:3])
                ),
            )
        )

    @classmethod
    def get_by_name(cls, python_name: str) -> Python | None:
        # Ignore broken installations.
        with contextlib.suppress(ValueError):
            if python := ShutilWhichPythonProvider.find_python_by_name(python_name):
                return cls(python=python)

        if python := findpython.find(python_name):
            return cls(python=python)

        return None

    @classmethod
    def get_preferred_python(cls, config: Config, io: IO | None = None) -> Python:
        """
        Determine and return the "preferred" Python interpreter based on the provided
        configuration and optional input/output stream.

        This method first attempts to get the active Python interpreter if the configuration
        does not mandate using Poetry's Python. If an active interpreter is found, it is returned.
        Otherwise, the method defaults to retrieving the Poetry's Python interpreter (System Python).

        This method **does not** attempt to sort versions or determine Python version constraint
        compatibility.
        """
        io = io or NullIO()

        if not config.get("virtualenvs.use-poetry-python") and (
            active_python := Python.get_active_python()
        ):
            io.write_error_line(
                f"Found: {active_python.executable}", verbosity=Verbosity.VERBOSE
            )
            return active_python

        return cls.get_system_python()

    @classmethod
    def get_compatible_python(cls, poetry: Poetry, io: IO | None = None) -> Python:
        """
        Retrieve a compatible Python version based on the given poetry configuration
        and Python constraints derived from the project.

        This method iterates through all available Python candidates and checks if any
        match the supported Python constraint as defined in the specified poetry package.

        :param poetry: The poetry configuration containing package information,
                       including Python constraints.
        :param io: The input/output stream for error and status messages. Defaults
                   to a null I/O if not provided.
        :return: A Python instance representing a compatible Python version.
        :raises NoCompatiblePythonVersionFoundError: If no Python version matches
                the supported constraint.
        """
        io = io or NullIO()
        supported_python = poetry.package.python_constraint

        for python in cls.find_all():
            if python.version.allows_any(supported_python):
                io.write_error_line(
                    f"Using <c1>{python.name}</c1> ({python.patch_version})"
                )
                return python

        raise NoCompatiblePythonVersionFoundError(poetry.package.python_versions)
