from __future__ import annotations

from typing import ClassVar

from cleo.commands.command import Command
from cleo.io.inputs.argument import Argument


class HelpCommand(Command):
    name = "help"

    description = "Displays help for a command."

    arguments: ClassVar[list[Argument]] = [
        Argument(
            "command_name",
            required=False,
            description="The command name",
            default="help",
        )
    ]

    help = """\
The <info>{command_name}</info> command displays help for a given command:

  <info>{command_full_name} list</info>

To display the list of available commands, please use the <info>list</info> command.
"""

    _command = None

    def set_command(self, command: Command) -> None:
        self._command = command

    def configure(self) -> None:
        self.ignore_validation_errors()

        super().configure()

    def handle(self) -> int:
        from cleo.descriptors.text_descriptor import TextDescriptor

        if self._command is None:
            assert self._application is not None
            self._command = self._application.find(self.argument("command_name"))

        self.line("")
        TextDescriptor().describe(self._io, self._command)

        self._command = None

        return 0
