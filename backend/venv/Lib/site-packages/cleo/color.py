from __future__ import annotations

import os

from typing import ClassVar

from cleo.exceptions import CleoValueError


class Color:
    COLORS: ClassVar[dict[str, tuple[int, int]]] = {
        "black": (30, 40),
        "red": (31, 41),
        "green": (32, 42),
        "yellow": (33, 43),
        "blue": (34, 44),
        "magenta": (35, 45),
        "cyan": (36, 46),
        "light_gray": (37, 47),
        "default": (39, 49),
        "dark_gray": (90, 100),
        "light_red": (91, 101),
        "light_green": (92, 102),
        "light_yellow": (93, 103),
        "light_blue": (94, 104),
        "light_magenta": (95, 105),
        "light_cyan": (96, 106),
        "white": (97, 107),
    }

    AVAILABLE_OPTIONS: ClassVar[dict[str, dict[str, int]]] = {
        "bold": {"set": 1, "unset": 22},
        "dark": {"set": 2, "unset": 22},
        "italic": {"set": 3, "unset": 23},
        "underline": {"set": 4, "unset": 24},
        "blink": {"set": 5, "unset": 25},
        "reverse": {"set": 7, "unset": 27},
        "conceal": {"set": 8, "unset": 28},
    }

    def __init__(
        self,
        foreground: str = "",
        background: str = "",
        options: list[str] | None = None,
    ) -> None:
        self._foreground = self._parse_color(foreground, False)
        self._background = self._parse_color(background, True)

        self._options = {}
        for option in options or []:
            if option not in self.AVAILABLE_OPTIONS:
                raise ValueError(
                    f'"{option}" is not a valid color option. '
                    f"It must be one of {', '.join(self.AVAILABLE_OPTIONS)}"
                )

            self._options[option] = self.AVAILABLE_OPTIONS[option]

    def apply(self, text: str) -> str:
        return self.set() + text + self.unset()

    def set(self) -> str:
        codes = []

        if self._foreground:
            codes.append(self._foreground)

        if self._background:
            codes.append(self._background)

        for option in self._options.values():
            codes.append(str(option["set"]))

        if not codes:
            return ""

        return f"\033[{';'.join(codes)}m"

    def unset(self) -> str:
        codes = []

        if self._foreground:
            codes.append("39")

        if self._background:
            codes.append("49")

        for option in self._options.values():
            codes.append(str(option["unset"]))

        if not codes:
            return ""

        return f"\033[{';'.join(codes)}m"

    def _parse_color(self, color: str, background: bool) -> str:
        if not color:
            return ""

        if color.startswith("#"):
            color = color[1:]

            if len(color) == 3:
                color = color[0] * 2 + color[1] * 2 + color[2] * 2

            if len(color) != 6:
                raise CleoValueError(f'"{color}" is an invalid color')

            return ("4" if background else "3") + self._convert_hex_color_to_ansi(
                int(color, 16)
            )

        if color not in self.COLORS:
            raise CleoValueError(
                f'"{color}" is an invalid color.'
                f" It must be one of {', '.join(self.COLORS)}"
            )

        return str(self.COLORS[color][int(background)])

    def _convert_hex_color_to_ansi(self, color: int) -> str:
        r = (color >> 16) & 255
        g = (color >> 8) & 255
        b = color & 255

        if os.getenv("COLORTERM") != "truecolor":
            return str(self._degrade_hex_color_to_ansi(r, g, b))

        return f"8;2;{r};{g};{b}"

    def _degrade_hex_color_to_ansi(self, r: int, g: int, b: int) -> int:
        if round(self._get_saturation(r, g, b) / 50) == 0:
            return 0

        return (round(b / 255) << 2) | (round(g / 255) << 1) | round(r / 255)

    def _get_saturation(self, r: int, g: int, b: int) -> int:
        r_float = r / 255
        g_float = g / 255
        b_float = b / 255
        v = max(r_float, g_float, b_float)

        diff = v - min(r_float, g_float, b_float)
        if diff == 0:
            return 0

        return int(diff * 100 / v)
