from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from cleo.io.buffered_io import BufferedIO
from cleo.io.inputs.argv_input import ArgvInput
from cleo.io.inputs.string_input import StringInput
from cleo.io.outputs.buffered_output import BufferedOutput


if TYPE_CHECKING:
    from cleo.commands.command import Command
    from cleo.io.outputs.output import Verbosity


class CommandTester:
    """
    Eases the testing of console commands.
    """

    def __init__(self, command: Command) -> None:
        self._command = command
        self._io = BufferedIO()
        self._inputs: list[str] = []
        self._status_code: int | None = None

    @property
    def command(self) -> Command:
        return self._command

    @property
    def io(self) -> BufferedIO:
        return self._io

    @property
    def status_code(self) -> int | None:
        return self._status_code

    def execute(
        self,
        args: str = "",
        inputs: str | None = None,
        interactive: bool | None = None,
        verbosity: Verbosity | None = None,
        decorated: bool | None = None,
        supports_utf8: bool = True,
    ) -> int:
        """
        Executes the command
        """
        application = self._command.application

        input_: StringInput | ArgvInput = StringInput(args)
        if (
            application is not None
            and application.definition.has_argument("command")
            and self._command.name is not None
        ):
            name = self._command.name
            if " " in name:
                # If the command is namespaced we rearrange
                # the input to parse it as a single argument
                argv = [application.name, self._command.name, *input_._tokens]

                input_ = ArgvInput(argv)
            else:
                input_ = StringInput(name + " " + args)

        self._io.set_input(input_)
        assert isinstance(self._io.output, BufferedOutput)
        assert isinstance(self._io.error_output, BufferedOutput)
        self._io.output.set_supports_utf8(supports_utf8)
        self._io.error_output.set_supports_utf8(supports_utf8)

        if inputs is not None:
            self._io.input.set_stream(StringIO(inputs))

        if interactive is not None:
            self._io.interactive(interactive)

        if verbosity is not None:
            self._io.set_verbosity(verbosity)

        if decorated is not None:
            self._io.decorated(decorated)

        self._status_code = self._command.run(self._io)

        return self._status_code
