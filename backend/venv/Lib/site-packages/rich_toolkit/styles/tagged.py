from typing import Any, Generator, Iterable, List

from rich._loop import loop_first_last
from rich.console import Console
from rich.segment import Segment
from rich.style import Style

from .base import ANIMATION_STATUS, BaseStyle


class TaggedStyle(BaseStyle):
    def __init__(self, *args, **kwargs) -> None:
        self.tag_width = kwargs.pop("tag_width", 14)

        super().__init__(*args, **kwargs)

        self.padding = 2
        self.cursor_offset = self.tag_width + self.padding
        self.decoration_size = self.tag_width + self.padding

    def _render_tag(
        self,
        text: str,
        console: Console,
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        style_name = "tag.title" if metadata.get("title", False) else "tag"

        style = console.get_style(style_name)

        if text:
            text = f" {text} "

        left_padding = self.tag_width - len(text)
        left_padding = max(0, left_padding)

        yield Segment(" " * left_padding)
        yield Segment(text, style=style)
        yield Segment(" " * self.padding)

    def decorate(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animation_status: ANIMATION_STATUS = "no_animation",
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        if animation_status != "no_animation":
            yield from self.decorate_with_animation(
                lines=lines,
                console=console,
                animation_status=animation_status,
                **metadata,
            )

            return

        tag = metadata.get("tag", "")

        for first, last, line in loop_first_last(lines):
            text = tag if first else ""
            yield from self._render_tag(text, console=console, **metadata)
            yield from line

            if not last:
                yield Segment.line()

    def decorate_with_animation(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animation_status: ANIMATION_STATUS = "no_animation",
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        block = "█"
        block_length = 5
        colors = self._get_animation_colors(
            console, steps=block_length, animation_status=animation_status, **metadata
        )

        left_padding = self.tag_width - block_length
        left_padding = max(0, left_padding)

        self._animation_counter += 1

        for first, _, line in loop_first_last(lines):
            if first:
                yield Segment(" " * left_padding)

                for j in range(block_length):
                    color_index = (j + self._animation_counter) % len(colors)
                    yield Segment(block, style=Style(color=colors[color_index]))

            else:
                yield Segment(" " * self.tag_width)

            yield Segment(" " * self.padding)

            yield from line
            yield Segment.line()
