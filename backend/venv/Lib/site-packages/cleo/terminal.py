from __future__ import annotations

import os
import sys

from typing import NamedTuple


class TerminalSize(NamedTuple):
    width: int
    height: int


class Terminal:
    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        fallback: tuple[int, int] | None = None,
    ) -> None:
        self._width = width
        self._height = height
        self._fallback = TerminalSize(*(fallback or (80, 25)))

    @property
    def width(self) -> int:
        return self.size.width

    @property
    def height(self) -> int:
        return self.size.height

    @property
    def size(self) -> TerminalSize:
        return self._get_terminal_size()

    def _get_terminal_size(self) -> TerminalSize:
        if not (self._width is None or self._height is None):
            return TerminalSize(self._width, self._height)

        width = 0
        height = 0

        columns = os.environ.get("COLUMNS")
        if columns is not None and columns.isdigit():
            width = int(columns)
        lines = os.environ.get("LINES")
        if lines is not None and lines.isdigit():
            height = int(lines)

        if width <= 0 or height <= 0:
            try:
                os_size = os.get_terminal_size(sys.__stdout__.fileno())
                size = TerminalSize(*os_size)
            except (AttributeError, ValueError, OSError):
                # stdout is None, closed, detached, or not a terminal, or
                # os.get_terminal_size() is unsupported # noqa: ERA001
                size = self._fallback
            if width <= 0:
                width = size.width or self._fallback.width
            if height <= 0:
                height = size.height or self._fallback.height

        return TerminalSize(
            width if self._width is None else self._width,
            height if self._height is None else self._height,
        )
