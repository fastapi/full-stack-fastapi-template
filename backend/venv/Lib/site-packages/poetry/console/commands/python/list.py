from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from poetry.core.constraints.version import parse_constraint
from poetry.core.version.exceptions import InvalidVersionError

from poetry.config.config import Config
from poetry.console.commands.command import Command
from poetry.utils.env.python import Python


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option

    from poetry.utils.env.python.manager import PythonInfo


class PythonListCommand(Command):
    name = "python list"

    arguments: ClassVar[list[Argument]] = [
        argument("version", "Python version to search for.", optional=True)
    ]

    options: ClassVar[list[Option]] = [
        option(
            "all",
            "a",
            "List all versions, including those available for download.",
            flag=True,
        ),
        option(
            "implementation", "i", "Python implementation to search for.", flag=False
        ),
        option("managed", "m", "List only Poetry managed Python versions.", flag=True),
    ]

    description = (
        "Shows Python versions available for this environment."
        " (<warning>experimental feature</warning>)"
    )

    def handle(self) -> int:
        rows: list[PythonInfo] = []
        constraint = None

        if self.argument("version"):
            request = self.argument("version")
            version = f"~{request}" if request.count(".") < 2 else request
            try:
                constraint = parse_constraint(version)
            except (ValueError, InvalidVersionError):
                self.io.write_error_line(
                    f"<error>Invalid Python version requested <b>{request}</></error>"
                )
                return 1

        for info in Python.find_all_versions(
            constraint=constraint, implementation=self.option("implementation")
        ):
            rows.append(info)

        if self.option("all"):
            for info in Python.find_downloadable_versions(constraint):
                rows.append(info)

        rows.sort(
            key=lambda x: (x.major, x.minor, x.patch, x.implementation), reverse=True
        )

        table = self.table(style="compact")
        table.set_headers(
            [
                "<fg=magenta;options=bold>Version</>",
                "<fg=magenta;options=bold>Implementation</>",
                "<fg=magenta;options=bold>Manager</>",
                "<fg=magenta;options=bold>Path</>",
            ]
        )

        implementations = {"cpython": "CPython", "pypy": "PyPy"}
        python_installation_path = Config.create().python_installation_dir

        row_count = 0

        for pv in rows:
            version = f"{pv.major}.{pv.minor}.{pv.patch}"
            implementation = implementations.get(
                pv.implementation.lower(), pv.implementation
            )
            is_poetry_managed = (
                pv.executable is None
                or pv.executable.resolve().is_relative_to(python_installation_path)
            )

            if self.option("managed") and not is_poetry_managed:
                continue

            manager = (
                "<fg=blue>Poetry</>" if is_poetry_managed else "<fg=yellow>System</>"
            )
            path = (
                f"<fg=green>{pv.executable.as_posix()}</>"
                if pv.executable
                else "Available for download"
            )

            table.add_row(
                [
                    f"<c1>{version}</>",
                    f"<b>{implementation}</>",
                    f"{manager}",
                    f"{path}",
                ]
            )
            row_count += 1

        if row_count > 0:
            table.render()
        else:
            self.io.write_line("No Python installations found.")

        return 0
