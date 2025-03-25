from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument


class EnvUseCommand(Command):
    name = "env use"
    description = "Activates or creates a new virtualenv for the current project."

    arguments: ClassVar[list[Argument]] = [
        argument("python", "The python executable to use.")
    ]

    def handle(self) -> int:
        from poetry.utils.env import EnvManager

        manager = EnvManager(self.poetry, io=self.io)

        if self.argument("python") == "system":
            manager.deactivate()

            return 0

        env = manager.activate(self.argument("python"))

        self.line(f"Using virtualenv: <comment>{env.path}</>")

        return 0
