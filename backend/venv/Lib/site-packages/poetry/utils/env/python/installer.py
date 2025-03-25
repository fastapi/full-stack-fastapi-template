from __future__ import annotations

import dataclasses

from subprocess import CalledProcessError
from typing import TYPE_CHECKING
from typing import Literal

import pbs_installer as pbi

from poetry.core.constraints.version import Version

from poetry.config.config import Config
from poetry.console.exceptions import ConsoleMessage
from poetry.console.exceptions import PoetryRuntimeError
from poetry.utils.env.python import Python


if TYPE_CHECKING:
    from pathlib import Path


BAD_PYTHON_INSTALL_INFO = [
    "This could happen because you are missing platform dependencies required.",
    "Please refer to https://gregoryszorc.com/docs/python-build-standalone/main/running.html#runtime-requirements "
    "for more information about the necessary requirements.",
    "Please remove the failing Python installation using <c1>poetry python remove <version></> before continuing.",
]


class PythonInstallerError(Exception):
    pass


class PythonDownloadNotFoundError(PythonInstallerError, ValueError):
    pass


class PythonInstallationError(PythonInstallerError, ValueError):
    pass


@dataclasses.dataclass(frozen=True)
class PythonInstaller:
    request: str
    implementation: Literal["cpython", "pypy"] = dataclasses.field(default="cpython")
    free_threaded: bool = dataclasses.field(default=False)
    installation_directory: Path = dataclasses.field(
        init=False, default_factory=lambda: Config.create().python_installation_dir
    )

    @property
    def version(self) -> Version:
        try:
            pyver, _ = pbi.get_download_link(
                self.request,
                implementation=self.implementation,
                free_threaded=self.free_threaded,
            )
            return Version.from_parts(
                major=pyver.major, minor=pyver.minor, patch=pyver.micro
            )
        except ValueError:
            raise PythonDownloadNotFoundError(
                "No suitable standalone build found for the requested Python version."
            )

    def exists(self) -> bool:
        version = self.version
        bad_executables = set()

        for python in Python.find_poetry_managed_pythons():
            try:
                if python.implementation.lower() != self.implementation:
                    continue

                if version == python.version:
                    return True
            except CalledProcessError:
                bad_executables.add(python.executable)

        if bad_executables:
            raise PoetryRuntimeError(
                reason="One or more installed version do not work on your system. This is not a Poetry issue.",
                messages=[
                    ConsoleMessage("\n".join(e.as_posix() for e in bad_executables))
                    .indent("  - ")
                    .make_section("Failing Executables")
                    .wrap("info"),
                    *[
                        ConsoleMessage(m).wrap("warning")
                        for m in BAD_PYTHON_INSTALL_INFO
                    ],
                ],
            )

        return False

    def install(self) -> None:
        try:
            # this can be broken into download, and install_file if required to make
            # use of Poetry's own mechanics for download and unpack
            pbi.install(
                self.request,
                self.installation_directory,
                version_dir=True,
                implementation=self.implementation,
                free_threaded=self.free_threaded,
            )
        except ValueError:
            raise PythonInstallationError(
                "Failed to download and install requested version of Python."
            )
