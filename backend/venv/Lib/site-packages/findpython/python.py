from __future__ import annotations

import dataclasses as dc
import logging
import os
import subprocess
from functools import lru_cache
from pathlib import Path

from packaging.version import InvalidVersion, Version

from findpython.utils import get_binary_hash

logger = logging.getLogger("findpython")
GET_VERSION_TIMEOUT = float(os.environ.get("FINDPYTHON_GET_VERSION_TIMEOUT", 5))


@lru_cache(maxsize=1024)
def _run_script(executable: str, script: str, timeout: float | None = None) -> str:
    """Run a script and return the output."""
    command = [executable, "-EsSc", script]
    logger.debug("Running script: %s", command)
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
        check=True,
        text=True,
    ).stdout


@dc.dataclass
class PythonVersion:
    """The single Python version object found by pythonfinder."""

    executable: Path
    _version: Version | None = None
    _architecture: str | None = None
    _interpreter: Path | None = None
    keep_symlink: bool = False

    def is_valid(self) -> bool:
        """Return True if the python is not broken."""
        try:
            v = self._get_version()
        except (
            OSError,
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            InvalidVersion,
        ):
            return False
        if self._version is None:
            self._version = v
        return True

    @property
    def real_path(self) -> Path:
        """Resolve the symlink if possible and return the real path."""
        try:
            return self.executable.resolve()
        except OSError:
            return self.executable

    @property
    def implementation(self) -> str:
        """Return the implementation of the python."""
        script = "import platform; print(platform.python_implementation())"
        return _run_script(str(self.executable), script).strip()

    @property
    def name(self) -> str:
        """Return the name of the python."""
        return self.executable.name

    @property
    def interpreter(self) -> Path:
        if self._interpreter is None:
            self._interpreter = Path(self._get_interpreter())
        return self._interpreter

    @property
    def version(self) -> Version:
        """Return the version of the python."""
        if self._version is None:
            self._version = self._get_version()
        return self._version

    @property
    def major(self) -> int:
        """Return the major version of the python."""
        return self.version.major

    @property
    def minor(self) -> int:
        """Return the minor version of the python."""
        return self.version.minor

    @property
    def patch(self) -> int:
        """Return the micro version of the python."""
        return self.version.micro

    @property
    def is_prerelease(self) -> bool:
        """Return True if the python is a prerelease."""
        return self.version.is_prerelease

    @property
    def is_devrelease(self) -> bool:
        """Return True if the python is a devrelease."""
        return self.version.is_devrelease

    @property
    def architecture(self) -> str:
        if not self._architecture:
            self._architecture = self._get_architecture()
        return self._architecture

    def binary_hash(self) -> str:
        """Return the binary hash of the python."""
        return get_binary_hash(self.real_path)

    def matches(
        self,
        major: int | None = None,
        minor: int | None = None,
        patch: int | None = None,
        pre: bool | None = None,
        dev: bool | None = None,
        name: str | None = None,
        architecture: str | None = None,
        implementation: str | None = None,
    ) -> bool:
        """
        Return True if the python matches the provided criteria.

        :param major: The major version to match.
        :type major: int
        :param minor: The minor version to match.
        :type minor: int
        :param patch: The micro version to match.
        :type patch: int
        :param pre: Whether the python is a prerelease.
        :type pre: bool
        :param dev: Whether the python is a devrelease.
        :type dev: bool
        :param name: The name of the python.
        :type name: str
        :param architecture: The architecture of the python.
        :type architecture: str
        :param implementation: The implementation of the python.
        :type implementation: str
        :return: Whether the python matches the provided criteria.
        :rtype: bool
        """
        if major is not None and self.major != major:
            return False
        if minor is not None and self.minor != minor:
            return False
        if patch is not None and self.patch != patch:
            return False
        if pre is not None and self.is_prerelease != pre:
            return False
        if dev is not None and self.is_devrelease != dev:
            return False
        if name is not None and self.name != name:
            return False
        if architecture is not None and self.architecture != architecture:
            return False
        if (
            implementation is not None
            and self.implementation.lower() != implementation.lower()
        ):
            return False
        return True

    def __hash__(self) -> int:
        return hash(self.executable)

    def __repr__(self) -> str:
        attrs = (
            "executable",
            "version",
            "architecture",
            "implementation",
            "major",
            "minor",
            "patch",
        )
        return "<PythonVersion {}>".format(
            ", ".join(f"{attr}={getattr(self, attr)!r}" for attr in attrs)
        )

    def __str__(self) -> str:
        return f"{self.implementation:>9}@{self.version}: {self.executable}"

    def _get_version(self) -> Version:
        """Get the version of the python."""
        script = "import platform; print(platform.python_version())"
        version = _run_script(
            str(self.executable), script, timeout=GET_VERSION_TIMEOUT
        ).strip()
        # Dev builds may produce version like `3.11.0+` and packaging.version
        # will reject it. Here we just remove the part after `+`
        # since it isn't critical for version comparison.
        version = version.split("+")[0]
        return Version(version)

    def _get_architecture(self) -> str:
        script = "import platform; print(platform.architecture()[0])"
        return _run_script(str(self.executable), script).strip()

    def _get_interpreter(self) -> str:
        script = "import sys; print(sys.executable)"
        return _run_script(str(self.executable), script).strip()

    def __lt__(self, other: PythonVersion) -> bool:
        """Sort by the version, then by length of the executable path."""
        return (
            self.version,
            int(self.architecture.startswith("64bit")),
            len(self.executable.as_posix()),
        ) < (
            other.version,
            int(other.architecture.startswith("64bit")),
            len(other.executable.as_posix()),
        )
