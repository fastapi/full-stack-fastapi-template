from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from cleo.commands.command import Command as BaseCommand
from cleo.exceptions import CleoValueError


if TYPE_CHECKING:
    from poetry.console.application import Application
    from poetry.poetry import Poetry


class Command(BaseCommand):
    loggers: ClassVar[list[str]] = []

    _poetry: Poetry | None = None

    @property
    def poetry(self) -> Poetry:
        if self._poetry is None:
            return self.get_application().poetry

        return self._poetry

    def set_poetry(self, poetry: Poetry) -> None:
        """Explicitly set the current Poetry.

        Useful for Plugins that extends the features of a Poetry CLI Command.
        """

        self._poetry = poetry

    def get_application(self) -> Application:
        from poetry.console.application import Application

        application = self.application
        assert isinstance(application, Application)
        return application

    def reset_poetry(self) -> None:
        self.get_application().reset_poetry()

    def option(self, name: str, default: Any = None) -> Any:
        try:
            return super().option(name)
        except CleoValueError:
            return default
