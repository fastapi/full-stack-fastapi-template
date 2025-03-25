from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from cleo.application import Application
from cleo.commands.command import Command
from cleo.io.inputs.argument import Argument
from cleo.io.inputs.definition import Definition
from cleo.io.inputs.option import Option
from cleo.io.outputs.output import Type


if TYPE_CHECKING:
    from cleo.io.io import IO


class Descriptor:
    def describe(self, io: IO, obj: Any, **options: Any) -> None:
        self._io = io

        if isinstance(obj, Argument):
            self._describe_argument(obj, **options)
        elif isinstance(obj, Option):
            self._describe_option(obj, **options)
        elif isinstance(obj, Definition):
            self._describe_definition(obj, **options)
        elif isinstance(obj, Command):
            self._describe_command(obj, **options)
        elif isinstance(obj, Application):
            self._describe_application(obj, **options)

    def _write(self, content: str, decorated: bool = True) -> None:
        self._io.write(
            content, new_line=False, type=Type.NORMAL if decorated else Type.RAW
        )

    def _describe_argument(self, argument: Argument, **options: Any) -> None:
        raise NotImplementedError

    def _describe_option(self, option: Option, **options: Any) -> None:
        raise NotImplementedError

    def _describe_definition(self, definition: Definition, **options: Any) -> None:
        raise NotImplementedError

    def _describe_command(self, command: Command, **options: Any) -> None:
        raise NotImplementedError

    def _describe_application(self, application: Application, **options: Any) -> None:
        raise NotImplementedError
