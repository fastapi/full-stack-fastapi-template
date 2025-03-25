from __future__ import annotations


class TableStyle:
    """
    Defines styles for Table instances.
    """

    def __init__(self) -> None:
        self._padding_char = " "
        self._horizontal_outside_border_char = "-"
        self._horizontal_inside_border_char = "-"
        self._vertical_outside_border_char = "|"
        self._vertical_inside_border_char = "|"
        self._crossing_char = "+"
        self._crossing_top_right_char = "+"
        self._crossing_top_mid_char = "+"
        self._crossing_top_left_char = "+"
        self._crossing_mid_right_char = "+"
        self._crossing_bottom_right_char = "+"
        self._crossing_bottom_mid_char = "+"
        self._crossing_bottom_left_char = "+"
        self._crossing_mid_left_char = "+"
        self._crossing_top_left_bottom_char = "+"
        self._crossing_top_mid_bottom_char = "+"
        self._crossing_top_right_bottom_char = "+"
        self._header_title_format = "<b> {} </b>"
        self._footer_title_format = "<b> {} </b>"
        self._cell_header_format = "<c1>{}</c1>"
        self._cell_row_format = "{}"
        self._cell_row_content_format = " {} "
        self._border_format = "{}"
        self._pad_type = "right"

    @property
    def padding_char(self) -> str:
        return self._padding_char

    @property
    def border_chars(self) -> list[str]:
        return [
            self._horizontal_outside_border_char,
            self._vertical_outside_border_char,
            self._horizontal_inside_border_char,
            self._vertical_inside_border_char,
        ]

    @property
    def crossing_char(self) -> str:
        return self._crossing_char

    @property
    def crossing_chars(self) -> list[str]:
        return [
            self._crossing_char,
            self._crossing_top_left_char,
            self._crossing_top_mid_char,
            self._crossing_top_right_char,
            self._crossing_mid_right_char,
            self._crossing_bottom_right_char,
            self._crossing_bottom_mid_char,
            self._crossing_bottom_left_char,
            self._crossing_mid_left_char,
            self._crossing_top_left_bottom_char,
            self._crossing_top_mid_bottom_char,
            self._crossing_top_right_bottom_char,
        ]

    @property
    def cell_header_format(self) -> str:
        return self._cell_header_format

    @property
    def cell_row_format(self) -> str:
        return self._cell_row_format

    @property
    def cell_row_content_format(self) -> str:
        return self._cell_row_content_format

    @property
    def border_format(self) -> str:
        return self._border_format

    @property
    def header_title_format(self) -> str:
        return self._header_title_format

    @property
    def footer_title_format(self) -> str:
        return self._footer_title_format

    @property
    def pad_type(self) -> str:
        return self._pad_type

    def set_padding_char(self, padding_char: str) -> TableStyle:
        """
        Sets padding character, used for cell padding.
        """
        if not padding_char:
            raise ValueError("The padding char must not be empty.")

        self._padding_char = padding_char

        return self

    def set_horizontal_border_chars(
        self, outside: str, inside: str | None = None
    ) -> TableStyle:
        """
        Sets horizontal border characters.

        ╔═══════════════╤══════════════════════════╤══════════════════╗
        1 ISBN          2 Title                    │ Author           ║
        ╠═══════════════╪══════════════════════════╪══════════════════╣
        ║ 99921-58-10-7 │ Divine Comedy            │ Dante Alighieri  ║
        ║ 9971-5-0210-0 │ A Tale of Two Cities     │ Charles Dickens  ║
        ║ 960-425-059-0 │ The Lord of the Rings    │ J. R. R. Tolkien ║
        ║ 80-902734-1-6 │ And Then There Were None │ Agatha Christie  ║
        ╚═══════════════╧══════════════════════════╧══════════════════╝
        """
        self._horizontal_outside_border_char = outside
        self._horizontal_inside_border_char = outside if inside is None else inside

        return self

    def set_vertical_border_chars(
        self, outside: str, inside: str | None = None
    ) -> TableStyle:
        """
        Sets vertical border characters.

        ╔═══════════════╤══════════════════════════╤══════════════════╗
        ║ ISBN          │ Title                    │ Author           ║
        ╠═══════1═══════╪══════════════════════════╪══════════════════╣
        ║ 99921-58-10-7 │ Divine Comedy            │ Dante Alighieri  ║
        ║ 9971-5-0210-0 │ A Tale of Two Cities     │ Charles Dickens  ║
        ╟───────2───────┼──────────────────────────┼──────────────────╢
        ║ 960-425-059-0 │ The Lord of the Rings    │ J. R. R. Tolkien ║
        ║ 80-902734-1-6 │ And Then There Were None │ Agatha Christie  ║
        ╚═══════════════╧══════════════════════════╧══════════════════╝
        """
        self._vertical_outside_border_char = outside
        self._vertical_inside_border_char = outside if inside is None else inside

        return self

    def set_crossing_chars(
        self,
        cross: str,
        top_left: str,
        top_mid: str,
        top_right: str,
        mid_right: str,
        bottom_right: str,
        bottom_mid: str,
        bottom_left: str,
        mid_left: str,
        top_left_bottom: str | None = None,
        top_mid_bottom: str | None = None,
        top_right_bottom: str | None = None,
    ) -> TableStyle:
        """
        Sets crossing characters.

        Example:

        1═══════════════2══════════════════════════2══════════════════3
        ║ ISBN          │ Title                    │ Author           ║
        8'══════════════0'═════════════════════════0'═════════════════4'
        ║ 99921-58-10-7 │ Divine Comedy            │ Dante Alighieri  ║
        ║ 9971-5-0210-0 │ A Tale of Two Cities     │ Charles Dickens  ║
        8───────────────0──────────────────────────0──────────────────4
        ║ 960-425-059-0 │ The Lord of the Rings    │ J. R. R. Tolkien ║
        ║ 80-902734-1-6 │ And Then There Were None │ Agatha Christie  ║
        7═══════════════6══════════════════════════6══════════════════5
        """
        self._crossing_char = cross
        self._crossing_top_left_char = top_left
        self._crossing_top_mid_char = top_mid
        self._crossing_top_right_char = top_right
        self._crossing_mid_right_char = mid_right
        self._crossing_bottom_right_char = bottom_right
        self._crossing_bottom_mid_char = bottom_mid
        self._crossing_bottom_left_char = bottom_left
        self._crossing_mid_left_char = mid_left
        self._crossing_top_left_bottom_char = (
            mid_left if top_left_bottom is None else top_left_bottom
        )
        self._crossing_top_mid_bottom_char = (
            cross if top_mid_bottom is None else top_mid_bottom
        )
        self._crossing_top_right_bottom_char = (
            mid_right if top_right_bottom is None else top_right_bottom
        )

        return self

    def set_default_crossing_char(self, char: str) -> TableStyle:
        """
        Sets default crossing character used for each cross.
        """
        return self.set_crossing_chars(
            char, char, char, char, char, char, char, char, char
        )

    def set_cell_header_format(self, cell_header_format: str) -> TableStyle:
        """
        Sets the header cell format.
        """
        self._cell_header_format = cell_header_format

        return self

    def set_cell_row_format(self, cell_row_format: str) -> TableStyle:
        """
        Sets the row cell format.
        """
        self._cell_row_format = cell_row_format

        return self

    def set_cell_row_content_format(self, cell_row_content_format: str) -> TableStyle:
        """
        Sets the row cell content format.
        """
        self._cell_row_content_format = cell_row_content_format

        return self

    def set_border_format(self, border_format: str) -> TableStyle:
        """
        Sets the border format.
        """
        self._border_format = border_format

        return self

    def set_header_title_format(self, header_title_format: str) -> TableStyle:
        """
        Sets the header title format.
        """
        self._header_title_format = header_title_format

        return self

    def set_footer_title_format(self, footer_title_format: str) -> TableStyle:
        """
        Sets the footer title format.
        """
        self._footer_title_format = footer_title_format

        return self

    def set_pad_type(self, pad_type: str) -> TableStyle:
        """
        Sets the padding type.
        """
        if pad_type not in {"left", "right", "center"}:
            raise ValueError(
                'Invalid padding type. Expected one of "left", "right", "center").'
            )

        self._pad_type = pad_type

        return self

    def pad(self, string: str, length: int, char: str = " ") -> str:
        if self._pad_type == "left":
            return string.rjust(length, char)

        if self._pad_type == "right":
            return string.ljust(length, char)

        return string.center(length, char)
