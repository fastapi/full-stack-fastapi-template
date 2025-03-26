from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import option

from poetry.console.commands.installer_command import InstallerCommand


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option


class LockCommand(InstallerCommand):
    name = "lock"
    description = "Locks the project dependencies."

    options: ClassVar[list[Option]] = [
        option(
            "regenerate",
            None,
            "Ignore existing lock file"
            " and overwrite it with a new lock file created from scratch.",
        ),
    ]

    help = """
The <info>lock</info> command reads the <comment>pyproject.toml</> file from the
current directory, processes it, and locks the dependencies in the\
 <comment>poetry.lock</>
file.
By default, packages that have already been added to the lock file before
will not be updated.

<info>poetry lock</info>
"""

    loggers: ClassVar[list[str]] = ["poetry.repositories.pypi_repository"]

    def handle(self) -> int:
        self.installer.lock(update=self.option("regenerate"))

        return self.installer.run()
