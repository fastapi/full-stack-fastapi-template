from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from cleo.io.inputs.string_input import StringInput
from cleo.io.io import IO

from poetry.console.commands.add import AddCommand
from poetry.console.commands.self.self_command import SelfCommand


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class SelfUpdateCommand(SelfCommand):
    name = "self update"
    description = "Updates Poetry to the latest version."

    arguments: ClassVar[list[Argument]] = [
        argument(
            "version", "The version to update to.", optional=True, default="latest"
        )
    ]
    options: ClassVar[list[Option]] = [
        option("preview", None, "Allow the installation of pre-release versions."),
        option(
            "dry-run",
            None,
            "Output the operations but do not execute anything "
            "(implicitly enables --verbose).",
        ),
    ]
    help = """\
The <c1>self update</c1> command updates Poetry version in its current runtime \
environment.
"""

    def _system_project_handle(self) -> int:
        self.write("<info>Updating Poetry version ...</info>\n\n")
        application = self.get_application()
        add_command = application.find("add")
        assert isinstance(add_command, AddCommand)
        add_command.set_env(self.env)
        add_command.set_poetry(self.poetry)
        application.configure_installer_for_command(add_command, self.io)

        argv = ["add", f"poetry@{self.argument('version')}"]

        if self.option("dry-run"):
            argv.append("--dry-run")

        if self.option("preview"):
            argv.append("--allow-prereleases")

        exit_code: int = add_command.run(
            IO(
                StringInput(" ".join(argv)),
                self.io.output,
                self.io.error_output,
            )
        )
        return exit_code
