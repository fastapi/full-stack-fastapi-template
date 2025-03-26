from __future__ import annotations

import shutil

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from poetry.core.constraints.version.version import Version
from poetry.core.version.exceptions import InvalidVersionError

from poetry.config.config import Config
from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option
    from cleo.io.io import IO


class PythonRemoveCommand(Command):
    name = "python remove"

    arguments: ClassVar[list[Argument]] = [
        argument("python", "The python version to remove.", multiple=True)
    ]
    options: ClassVar[list[Option]] = [
        option(
            "implementation",
            "i",
            "Python implementation to use. (cpython, pypy)",
            flag=False,
            default="cpython",
        ),
    ]

    description = (
        "Remove the specified Python version if managed by Poetry."
        " (<warning>experimental feature</warning>)"
    )

    @staticmethod
    def remove_python_installation(request: str, implementation: str, io: IO) -> int:
        try:
            version = Version.parse(request)
        except (ValueError, InvalidVersionError):
            io.write_error_line(
                f"<error>Invalid Python version requested <b>{request}</></error>"
            )
            return 1

        if not (version.major and version.minor and version.patch):
            io.write_error_line(
                f"<error>Invalid Python version requested <b>{request}</></error>\n"
            )
            io.write_error_line(
                "You need to provide an exact Python version in the format <c1>X.Y.Z</> to be removed.\n\n"
                "You can use <c1>poetry python list -m</> to list installed Poetry managed Python versions."
            )

            return 1

        request_title = f"<c1>{request}</> (<b>{implementation}</>)"
        path = Config.create().python_installation_dir / f"{implementation}@{version}"

        if path.exists():
            if io.is_verbose():
                io.write_line(f"Installation path: {path}")

            io.write(f"Removing installation {request_title} ... ")

            try:
                shutil.rmtree(path)
            except OSError as e:
                io.write("<fg=red>Failed</>\n")

                if io.is_verbose():
                    io.write_line(f"Failed to remove directory: {e}")

            io.write("<fg=green>Done</>\n")
        else:
            io.write_line(f"No installation was found at {path}.")

        return 0

    def handle(self) -> int:
        implementation = self.option("implementation").lower()

        result = 0

        for request in self.argument("python"):
            result += self.remove_python_installation(request, implementation, self.io)

        return result
