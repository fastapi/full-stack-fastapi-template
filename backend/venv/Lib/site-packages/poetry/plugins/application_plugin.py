from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.plugins.base_plugin import BasePlugin


if TYPE_CHECKING:
    from poetry.console.application import Application
    from poetry.console.commands.command import Command


class ApplicationPlugin(BasePlugin):
    """
    Base class for application plugins.
    """

    group = "poetry.application.plugin"

    @property
    def commands(self) -> list[type[Command]]:
        return []

    def activate(self, application: Application) -> None:
        for command in self.commands:
            assert command.name is not None
            application.command_loader.register_factory(command.name, command)
