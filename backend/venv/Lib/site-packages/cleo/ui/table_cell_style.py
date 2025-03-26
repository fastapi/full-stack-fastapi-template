from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 8):
        from typing import Literal
    else:
        from typing_extensions import Literal

    _Align = Literal["left", "right"]


class TableCellStyle:
    def __init__(
        self,
        fg: str = "default",
        bg: str = "default",
        options: list[str] | None = None,
        align: _Align = "left",
        cell_format: str | None = None,
    ) -> None:
        self._fg = fg
        self._bg = bg
        self._options = options
        self._align = "left"
        self._cell_format = cell_format

    @property
    def cell_format(self) -> str | None:
        return self._cell_format

    @property
    def tag(self) -> str:
        tag = "<fg={};bg={}"

        if self._options:
            tag += f";options={','.join(self._options)}"

        tag += ">"

        return tag

    def pad(self, string: str, length: int, char: str = " ") -> str:
        if self._align == "left":
            return string.rjust(length, char)

        if self._align == "right":
            return string.ljust(length, char)

        return string.center(length, char)
