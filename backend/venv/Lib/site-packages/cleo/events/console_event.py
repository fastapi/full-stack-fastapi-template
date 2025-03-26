from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.events.event import Event


if TYPE_CHECKING:
    from cleo.commands.command import Command
    from cleo.io.io import IO


class ConsoleEvent(Event):
    """
    An event that gives access to the IO of a command.
    """

    def __init__(self, command: Command, io: IO) -> None:
        super().__init__()

        self._command = command
        self._io = io

    @property
    def command(self) -> Command:
        return self._command

    @property
    def io(self) -> IO:
        return self._io
