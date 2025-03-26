from typing import Any, Generator, Iterable, List

from rich._loop import loop_first_last
from rich.console import (
    Console,
)
from rich.segment import Segment
from rich.style import Style
from rich.text import Text


from .base import ANIMATION_STATUS, BaseStyle


class MinimalStyle(BaseStyle):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.cursor_offset = 2
        self.decoration_size = 2

    def decorate(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animation_status: ANIMATION_STATUS = "no_animation",
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        if animation_status != "no_animation":
            block = "●"
            colors = self._get_animation_colors(
                console, animation_status=animation_status, **metadata
            )

            self._animation_counter += 1

            color_index = self._animation_counter % len(colors)

            for first, last, line in loop_first_last(lines):
                if first:
                    yield Segment(f"{block} ", style=Style(color=colors[color_index]))
                else:
                    yield Segment(" " * 2)
                yield from line
                yield Segment.line()

            return

        for first, last, line in loop_first_last(lines):
            decoration = " " * 2

            yield Segment(decoration)
            yield from line

            if not last:
                yield Segment.line()

    def empty_line(self) -> Text:
        return Text("")
