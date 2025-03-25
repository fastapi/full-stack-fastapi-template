from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from cleo.ui.table_cell_style import TableCellStyle


class TableCell(str):
    def __new__(
        cls,
        value: str = "",
        rowspan: int = 1,
        colspan: int = 1,
        style: TableCellStyle | None = None,
    ) -> TableCell:
        return super().__new__(cls, value)

    def __init__(
        self,
        value: str = "",
        rowspan: int = 1,
        colspan: int = 1,
        style: TableCellStyle | None = None,
    ) -> None:
        self._rowspan = rowspan
        self._colspan = colspan
        self._style = style

    @property
    def rowspan(self) -> int:
        return self._rowspan

    @property
    def colspan(self) -> int:
        return self._colspan

    @property
    def style(self) -> TableCellStyle | None:
        return self._style
