from __future__ import annotations

import math

from typing import TYPE_CHECKING
from typing import TextIO

from cleo.io.outputs.output import Verbosity
from cleo.io.outputs.stream_output import StreamOutput
from cleo.terminal import Terminal


if TYPE_CHECKING:
    from cleo.formatters.formatter import Formatter


class SectionOutput(StreamOutput):
    def __init__(
        self,
        stream: TextIO,
        sections: list[SectionOutput],
        verbosity: Verbosity = Verbosity.NORMAL,
        decorated: bool | None = None,
        formatter: Formatter | None = None,
    ) -> None:
        super().__init__(
            stream, verbosity=verbosity, decorated=decorated, formatter=formatter
        )

        self._content: list[str] = []
        self._lines = 0
        sections.insert(0, self)
        self._sections = sections
        self._terminal = Terminal().size

    @property
    def content(self) -> str:
        return "".join(self._content)

    @property
    def lines(self) -> int:
        return self._lines

    def clear(self, lines: int | None = None) -> None:
        if not (self._content and self.is_decorated()):
            return

        if lines:
            # Multiply lines by 2 to cater for each new line added between content
            del self._content[-lines * 2 :]
        else:
            lines = self._lines
            self._content = []

        self._lines -= lines

        super()._write(
            self._pop_stream_content_until_current_section(lines), new_line=False
        )

    def overwrite(self, message: str) -> None:
        self.clear()
        self.write_line(message)

    def add_content(self, content: str) -> None:
        for line_content in content.split("\n"):
            self._lines += (
                math.ceil(
                    len(self.remove_format(line_content).replace("\t", " " * 8))
                    / self._terminal.width
                )
                or 1
            )
            self._content.append(line_content)
            self._content.append("\n")

    def _write(self, message: str, new_line: bool = False) -> None:
        if not self.is_decorated():
            return super()._write(message, new_line=new_line)

        erased_content = self._pop_stream_content_until_current_section()

        self.add_content(message)

        super()._write(message, new_line=True)
        super()._write(erased_content, new_line=False)

    def _pop_stream_content_until_current_section(
        self, lines_to_clear_count: int = 0
    ) -> str:
        erased_content = []

        for section in self._sections:
            if section is self:
                break

            lines_to_clear_count += section.lines
            erased_content.append(section.content)

        if lines_to_clear_count > 0:
            # Move cursor up n lines
            super()._write(f"\x1b[{lines_to_clear_count}A", new_line=False)
            # Erase to end of screen
            super()._write("\x1b[0J", new_line=False)

        return "".join(reversed(erased_content))
