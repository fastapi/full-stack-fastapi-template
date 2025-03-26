from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from poetry.core.constraints.version.version import Version
from poetry.core.version.exceptions import InvalidVersionError

from poetry.console.commands.command import Command
from poetry.console.commands.python.remove import PythonRemoveCommand
from poetry.console.exceptions import PoetryRuntimeError
from poetry.utils.env.python.installer import PythonDownloadNotFoundError
from poetry.utils.env.python.installer import PythonInstallationError
from poetry.utils.env.python.installer import PythonInstaller
from poetry.utils.env.python.providers import PoetryPythonPathProvider


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class PythonInstallCommand(Command):
    name = "python install"

    arguments: ClassVar[list[Argument]] = [
        argument("python", "The python version to install.")
    ]

    options: ClassVar[list[Option]] = [
        option("clean", "c", "Clean up installation if check fails.", flag=True),
        option(
            "free-threaded", "t", "Use free-threaded version if available.", flag=True
        ),
        option(
            "implementation",
            "i",
            "Python implementation to use. (cpython, pypy)",
            flag=False,
            default="cpython",
        ),
        option(
            "reinstall", "r", "Reinstall if installation already exists.", flag=True
        ),
    ]

    description = (
        "Install the specified Python version from the Python Standalone Builds project."
        " (<warning>experimental feature</warning>)"
    )

    def handle(self) -> int:
        request = self.argument("python")
        impl = self.option("implementation").lower()
        reinstall = self.option("reinstall")
        free_threaded = self.option("free-threaded")

        try:
            version = Version.parse(request)
        except (ValueError, InvalidVersionError):
            self.io.write_error_line(
                f"<error>Invalid Python version requested <b>{request}</></error>"
            )
            return 1

        if free_threaded and version < Version.parse("3.13.0"):
            self.io.write_error_line("")
            self.io.write_error_line(
                "Free threading is not supported for Python versions prior to <c1>3.13.0</>.\n\n"
                "See https://docs.python.org/3/howto/free-threading-python.html for more information."
            )
            self.io.write_error_line("")
            return 1

        installer = PythonInstaller(request, impl, free_threaded)

        try:
            if installer.exists() and not reinstall:
                self.io.write_error_line(
                    "Python version already installed at "
                    f"<b>{PoetryPythonPathProvider.installation_dir(version, impl)}</>.\n"
                )
                self.io.write_error_line(
                    f"Use <c1>--reinstall</> to install anyway, "
                    f"or use <c1>poetry python remove {version}</> first."
                )
                return 1
        except PythonDownloadNotFoundError:
            self.io.write_error_line(
                "No suitable standalone build found for the requested Python version."
            )
            return 1

        add_info = impl
        if free_threaded:
            add_info += ", free-threaded"
        request_title = f"<c1>{request}</> (<b>{add_info}</>)"

        try:
            self.io.write(f"Downloading and installing {request_title} ... ")
            installer.install()
        except PythonInstallationError as e:
            self.io.write("<fg=red>Failed</>\n")
            self.io.write_error_line("")
            self.io.write_error_line(str(e))
            self.io.write_error_line("")
            return 1

        self.io.write("<fg=green>Done</>\n")
        self.io.write(f"Testing {request_title} ... ")

        try:
            installer.exists()
        except PoetryRuntimeError as e:
            self.io.write("<fg=red>Failed</>\n")

            if installer.installation_directory.exists() and self.option("clean"):
                PythonRemoveCommand.remove_python_installation(
                    str(installer.version), impl, self.io
                )

            raise e

        self.io.write("<fg=green>Done</>\n")

        return 0
