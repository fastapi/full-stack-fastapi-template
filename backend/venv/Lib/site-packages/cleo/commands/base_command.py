from __future__ import annotations

import inspect

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.exceptions import CleoError
from cleo.io.inputs.definition import Definition


if TYPE_CHECKING:
    from cleo.application import Application
    from cleo.io.io import IO


class BaseCommand:
    name: str | None = None

    description = ""

    help = ""

    enabled = True
    hidden = False

    usages: ClassVar[list[str]] = []

    def __init__(self) -> None:
        self._definition = Definition()
        self._full_definition: Definition | None = None
        self._application: Application | None = None
        self._ignore_validation_errors = False
        self._synopsis: dict[str, str] = {}

        self.configure()

        for i, usage in enumerate(self.usages):
            if self.name and not usage.startswith(self.name):
                self.usages[i] = f"{self.name} {usage}"

    @property
    def application(self) -> Application | None:
        return self._application

    @property
    def definition(self) -> Definition:
        if self._full_definition is not None:
            return self._full_definition

        return self._definition

    @property
    def processed_help(self) -> str:
        help_text = self.help
        if not self.help:
            help_text = self.description

        is_single_command = self._application and self._application.is_single_command()

        if self._application:
            current_script = self._application.name
        else:
            current_script = inspect.stack()[-1][1]

        return help_text.format(
            command_name=self.name,
            command_full_name=current_script
            if is_single_command
            else f"{current_script} {self.name}",
            script_name=current_script,
        )

    def ignore_validation_errors(self) -> None:
        self._ignore_validation_errors = True

    def set_application(self, application: Application | None = None) -> None:
        self._application = application

        self._full_definition = None

    def configure(self) -> None:
        """
        Configures the current command.
        """

    def execute(self, io: IO) -> int:
        raise NotImplementedError

    def interact(self, io: IO) -> None:
        """
        Interacts with the user.
        """

    def initialize(self, io: IO) -> None:
        pass

    def run(self, io: IO) -> int:
        self.merge_application_definition()

        try:
            io.input.bind(self.definition)
        except CleoError:
            if not self._ignore_validation_errors:
                raise

        self.initialize(io)

        if io.is_interactive():
            self.interact(io)

        if io.input.has_argument("command") and io.input.argument("command") is None:
            io.input.set_argument("command", self.name)

        io.input.validate()

        return self.execute(io) or 0

    def merge_application_definition(self, merge_args: bool = True) -> None:
        if self._application is None:
            return

        self._full_definition = Definition()
        self._full_definition.add_options(self._definition.options)
        self._full_definition.add_options(self._application.definition.options)

        if merge_args:
            self._full_definition.set_arguments(self._application.definition.arguments)
            self._full_definition.add_arguments(self._definition.arguments)
        else:
            self._full_definition.set_arguments(self._definition.arguments)

    def synopsis(self, short: bool = False) -> str:
        key = "short" if short else "long"

        if key not in self._synopsis:
            self._synopsis[key] = f"{self.name} {self.definition.synopsis(short)}"

        return self._synopsis[key]
