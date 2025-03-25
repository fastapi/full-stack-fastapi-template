from __future__ import annotations

from cleo.exceptions import CleoValueError
from cleo.formatters.style import Style


class StyleStack:
    def __init__(self, empty_style: Style | None = None) -> None:
        if empty_style is None:
            empty_style = Style()

        self._empty_style = empty_style
        self._styles: list[Style] = []

    @property
    def current(self) -> Style:
        if not self._styles:
            return self._empty_style

        return self._styles[-1]

    def reset(self) -> None:
        self._styles = []

    def push(self, style: Style) -> None:
        self._styles.append(style)

    def pop(self, style: Style | None = None) -> Style:
        if not self._styles:
            return self._empty_style

        if style is None:
            return self._styles.pop()

        sample = style.apply("")

        for i, stacked_style in reversed(list(enumerate(self._styles))):
            if sample == stacked_style.apply(""):
                self._styles = self._styles[:i]
                return stacked_style

        raise CleoValueError("Invalid nested tag found")
