from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from typing import Iterable

from cleo._utils import strip_tags
from cleo.formatters.formatter import Formatter


if TYPE_CHECKING:
    from cleo.io.outputs.section_output import SectionOutput


class Verbosity(Enum):
    QUIET: int = 16
    NORMAL: int = 32
    VERBOSE: int = 64
    VERY_VERBOSE: int = 128
    DEBUG: int = 256


class Type(Enum):
    NORMAL: int = 1
    RAW: int = 2
    PLAIN: int = 4


class Output:
    def __init__(
        self,
        verbosity: Verbosity = Verbosity.NORMAL,
        decorated: bool = False,
        formatter: Formatter | None = None,
    ) -> None:
        self._verbosity: Verbosity = verbosity
        self._formatter = formatter or Formatter()
        self._formatter.decorated(decorated)

        self._section_outputs: list[SectionOutput] = []

    @property
    def formatter(self) -> Formatter:
        return self._formatter

    @property
    def verbosity(self) -> Verbosity:
        return self._verbosity

    def set_formatter(self, formatter: Formatter) -> None:
        self._formatter = formatter

    def is_decorated(self) -> bool:
        return self._formatter.is_decorated()

    def decorated(self, decorated: bool = True) -> None:
        self._formatter.decorated(decorated)

    def supports_utf8(self) -> bool:
        """
        Returns whether the stream supports the UTF-8 encoding.
        """
        return True

    def set_verbosity(self, verbosity: Verbosity) -> None:
        self._verbosity = verbosity

    def is_quiet(self) -> bool:
        return self._verbosity is Verbosity.QUIET

    def is_verbose(self) -> bool:
        return self._verbosity.value >= Verbosity.VERBOSE.value

    def is_very_verbose(self) -> bool:
        return self._verbosity.value >= Verbosity.VERY_VERBOSE.value

    def is_debug(self) -> bool:
        return self._verbosity is Verbosity.DEBUG

    def write_line(
        self,
        messages: str | Iterable[str],
        verbosity: Verbosity = Verbosity.NORMAL,
        type: Type = Type.NORMAL,
    ) -> None:
        self.write(messages, new_line=True, verbosity=verbosity, type=type)

    def write(
        self,
        messages: str | Iterable[str],
        new_line: bool = False,
        verbosity: Verbosity = Verbosity.NORMAL,
        type: Type = Type.NORMAL,
    ) -> None:
        if isinstance(messages, str):
            messages = [messages]

        if verbosity.value > self.verbosity.value:
            return

        for message in messages:
            if type is Type.NORMAL:
                message = self._formatter.format(message)
            elif type is Type.PLAIN:
                message = strip_tags(self._formatter.format(message))

            self._write(message, new_line=new_line)

    def flush(self) -> None:
        pass

    def remove_format(self, text: str) -> str:
        return self.formatter.remove_format(text)

    def section(self) -> SectionOutput:
        raise NotImplementedError

    def _write(self, message: str, new_line: bool = False) -> None:
        raise NotImplementedError
