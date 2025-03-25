from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from cleo.commands.command import Command


class CommandLoader:
    @property
    def names(self) -> list[str]:
        """
        All registered command names.
        """
        raise NotImplementedError

    def get(self, name: str) -> Command:
        """
        Loads a command.
        """
        raise NotImplementedError

    def has(self, name: str) -> bool:
        """
        Checks whether a command exists or not.
        """
        raise NotImplementedError
