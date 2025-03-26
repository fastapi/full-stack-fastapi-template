from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.events.console_event import ConsoleEvent


if TYPE_CHECKING:
    from cleo.commands.command import Command
    from cleo.io.io import IO


class ConsoleCommandEvent(ConsoleEvent):
    """
    An event triggered before the command is executed.

    It allows to do things like skipping the command or changing the input.
    """

    RETURN_CODE_DISABLED: int = 113

    def __init__(self, command: Command, io: IO) -> None:
        super().__init__(command, io)

        self._command_should_run = True

    def disable_command(self) -> None:
        self._command_should_run = False

    def enable_command(self) -> None:
        self._command_should_run = True

    def command_should_run(self) -> bool:
        return self._command_should_run
