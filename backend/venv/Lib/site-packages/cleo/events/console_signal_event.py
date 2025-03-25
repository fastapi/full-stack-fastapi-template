from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.events.console_event import ConsoleEvent


if TYPE_CHECKING:
    import signal

    from cleo.commands.command import Command
    from cleo.io.io import IO


class ConsoleSignalEvent(ConsoleEvent):
    """
    An event triggered by a system signal.
    """

    def __init__(
        self, command: Command, io: IO, handling_signal: signal.Signals
    ) -> None:
        super().__init__(command, io)
        self._handling_signal = handling_signal

    @property
    def handling_signal(self) -> signal.Signals:
        return self._handling_signal
