from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from cleo.io.inputs.string_input import StringInput
from cleo.io.io import IO
from cleo.io.outputs.buffered_output import BufferedOutput


if TYPE_CHECKING:
    from cleo.io.inputs.input import Input


class BufferedIO(IO):
    def __init__(
        self,
        input: Input | None = None,
        decorated: bool = False,
        supports_utf8: bool = True,
    ) -> None:
        super().__init__(
            input or StringInput(""),
            BufferedOutput(decorated=decorated, supports_utf8=supports_utf8),
            BufferedOutput(decorated=decorated, supports_utf8=supports_utf8),
        )

    def fetch_output(self) -> str:
        return cast(BufferedOutput, self._output).fetch()

    def fetch_error(self) -> str:
        return cast(BufferedOutput, self._error_output).fetch()

    def clear(self) -> None:
        cast(BufferedOutput, self._output).clear()
        cast(BufferedOutput, self._error_output).clear()

    def clear_output(self) -> None:
        cast(BufferedOutput, self._output).clear()

    def clear_error(self) -> None:
        cast(BufferedOutput, self._error_output).clear()

    def supports_utf8(self) -> bool:
        return cast(BufferedOutput, self._output).supports_utf8()

    def clear_user_input(self) -> None:
        self._input.stream.truncate(0)
        self._input.stream.seek(0)

    def set_user_input(self, user_input: str) -> None:
        self.clear_user_input()

        self._input.stream.write(user_input)
        self._input.stream.seek(0)
