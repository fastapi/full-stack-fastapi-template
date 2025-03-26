from __future__ import annotations

import codecs
import io
import locale
import os
import sys

from typing import TYPE_CHECKING
from typing import TextIO
from typing import cast

from cleo.io.outputs.output import Output
from cleo.io.outputs.output import Verbosity


if TYPE_CHECKING:
    from cleo.formatters.formatter import Formatter
    from cleo.io.outputs.section_output import SectionOutput


class StreamOutput(Output):
    FILE_TYPE_CHAR = 0x0002
    FILE_TYPE_REMOTE = 0x8000
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    def __init__(
        self,
        stream: TextIO,
        verbosity: Verbosity = Verbosity.NORMAL,
        decorated: bool | None = None,
        formatter: Formatter | None = None,
    ) -> None:
        self._stream = stream
        self._supports_utf8 = self._get_utf8_support_info()
        super().__init__(
            verbosity=verbosity,
            decorated=decorated or self._has_color_support(),
            formatter=formatter,
        )

    @property
    def stream(self) -> TextIO:
        return self._stream

    def supports_utf8(self) -> bool:
        return self._supports_utf8

    def _get_utf8_support_info(self) -> bool:
        """
        Returns whether the stream supports the UTF-8 encoding.
        """
        encoding = self._stream.encoding or locale.getpreferredencoding(False)

        try:
            return codecs.lookup(encoding).name == "utf-8"
        except Exception:
            return True

    def flush(self) -> None:
        self._stream.flush()

    def section(self) -> SectionOutput:
        from cleo.io.outputs.section_output import SectionOutput

        return SectionOutput(
            self._stream,
            self._section_outputs,
            verbosity=self.verbosity,
            decorated=self.is_decorated(),
            formatter=self.formatter,
        )

    def _write(self, message: str, new_line: bool = False) -> None:
        if new_line:
            message += "\n"

        self._stream.write(message)
        self._stream.flush()

    def _has_color_support(self) -> bool:
        # Follow https://no-color.org/
        if "NO_COLOR" in os.environ:
            return False

        if os.getenv("TERM_PROGRAM") == "Hyper":
            return True

        if sys.platform == "win32":
            shell_supported = (
                os.getenv("ANSICON") is not None
                or os.getenv("ConEmuANSI") == "ON"  # noqa: SIM112
                or os.getenv("TERM") == "xterm"
            )

            if shell_supported:
                return True

            if not hasattr(self._stream, "fileno"):
                return False

            # Checking for Windows version
            # If we have a compatible version
            # activate color support
            windows_version = sys.getwindowsversion()
            major, build = windows_version[0], windows_version[2]
            if (major, build) < (10, 14393):
                return False

            # Activate colors if possible
            import ctypes
            import ctypes.wintypes

            kernel32 = ctypes.windll.kernel32

            fileno = self._stream.fileno()

            if fileno == 1:
                h = kernel32.GetStdHandle(-11)
            elif fileno == 2:
                h = kernel32.GetStdHandle(-12)
            else:
                return False

            if h is None or h == ctypes.wintypes.HANDLE(-1):
                return False

            if (
                kernel32.GetFileType(h) & ~self.FILE_TYPE_REMOTE
            ) != self.FILE_TYPE_CHAR:
                return False

            mode = ctypes.wintypes.DWORD()
            if not kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                return False

            if (mode.value & self.ENABLE_VIRTUAL_TERMINAL_PROCESSING) != 0:
                return True

            return cast(
                bool,
                kernel32.SetConsoleMode(
                    h, mode.value | self.ENABLE_VIRTUAL_TERMINAL_PROCESSING
                )
                != 0,
            )

        if not hasattr(self._stream, "fileno"):
            return False

        try:
            return os.isatty(self._stream.fileno())
        except io.UnsupportedOperation:
            return False
