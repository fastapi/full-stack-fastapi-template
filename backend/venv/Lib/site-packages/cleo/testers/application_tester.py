from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from cleo.io.buffered_io import BufferedIO
from cleo.io.inputs.string_input import StringInput
from cleo.io.outputs.buffered_output import BufferedOutput


if TYPE_CHECKING:
    from cleo.application import Application
    from cleo.io.outputs.output import Verbosity


class ApplicationTester:
    """
    Eases the testing of console applications.
    """

    def __init__(self, application: Application) -> None:
        self._application = application
        self._application.auto_exits(False)
        self._io = BufferedIO()
        self._status_code = 0

    @property
    def application(self) -> Application:
        return self._application

    @property
    def io(self) -> BufferedIO:
        return self._io

    @property
    def status_code(self) -> int:
        return self._status_code

    def execute(
        self,
        args: str = "",
        inputs: str | None = None,
        interactive: bool = True,
        verbosity: Verbosity | None = None,
        decorated: bool = False,
        supports_utf8: bool = True,
    ) -> int:
        """
        Executes the command
        """
        self._io.clear()

        self._io.set_input(StringInput(args))
        self._io.decorated(decorated)
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

        self._status_code = self._application.run(
            self._io.input,
            self._io.output,
            self._io.error_output,
        )

        return self._status_code
