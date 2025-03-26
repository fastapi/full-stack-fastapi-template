from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from cleo.io.outputs.output import Output
from cleo.io.outputs.output import Verbosity
from cleo.io.outputs.section_output import SectionOutput


if TYPE_CHECKING:
    from cleo.formatters.formatter import Formatter


class BufferedOutput(Output):
    def __init__(
        self,
        verbosity: Verbosity = Verbosity.NORMAL,
        decorated: bool = False,
        formatter: Formatter | None = None,
        supports_utf8: bool = True,
    ) -> None:
        super().__init__(decorated=decorated, verbosity=verbosity, formatter=formatter)

        self._buffer = StringIO()
        self._supports_utf8 = supports_utf8

    def fetch(self) -> str:
        """
        Empties the buffer and returns its content.
        """
        content = self._buffer.getvalue()
        self._buffer = StringIO()

        return content

    def clear(self) -> None:
        """
        Empties the buffer.
        """
        self._buffer = StringIO()

    def supports_utf8(self) -> bool:
        return self._supports_utf8

    def set_supports_utf8(self, supports_utf8: bool) -> None:
        self._supports_utf8 = supports_utf8

    def section(self) -> SectionOutput:
        return SectionOutput(
            self._buffer,
            self._section_outputs,
            verbosity=self.verbosity,
            decorated=self.is_decorated(),
            formatter=self.formatter,
        )

    def _write(self, message: str, new_line: bool = False) -> None:
        self._buffer.write(message)

        if new_line:
            self._buffer.write("\n")
