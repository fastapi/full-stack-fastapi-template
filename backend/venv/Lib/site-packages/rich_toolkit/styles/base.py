from abc import ABC, abstractmethod
from typing import Any, Generator, Iterable, List, Type, TypeVar

from rich.color import Color
from rich.console import (
    Console,
    ConsoleOptions,
    ConsoleRenderable,
    RenderableType,
    RenderResult,
)
from rich.segment import Segment
from rich.text import Text
from typing_extensions import Literal

from rich_toolkit.utils.colors import lighten

ConsoleRenderableClass = TypeVar(
    "ConsoleRenderableClass", bound=Type[ConsoleRenderable]
)


ANIMATION_STATUS = Literal["started", "stopped", "error", "no_animation"]


class BaseStyle(ABC):
    result_color: Color
    decoration_size: int

    def __init__(self) -> None:
        self.padding = 2
        self.cursor_offset = 0

        self._animation_counter = 0
        self.decoration_size = 2

    def empty_line(self) -> Text:
        return Text(" ")

    def with_decoration(
        self,
        *renderables: RenderableType,
        animation_status: ANIMATION_STATUS = "no_animation",
        **metadata: Any,
    ) -> ConsoleRenderable:
        class WithDecoration:
            @staticmethod
            def __rich_console__(
                console: Console, options: ConsoleOptions
            ) -> RenderResult:
                for content in renderables:
                    # our styles are potentially adding some paddings on the left
                    # and right sides, so we need to adjust the max_width to
                    # make sure that rich takes that into account
                    options = options.update(
                        max_width=console.width - self.decoration_size
                    )

                    lines = console.render_lines(content, options, pad=False)

                    for line in Segment.split_lines(
                        self.decorate(
                            lines=lines,
                            console=console,
                            animation_status=animation_status,
                            **metadata,
                        )
                    ):
                        yield from line
                        yield Segment.line()

        return WithDecoration()

    def decorate_class(
        self, klass: ConsoleRenderableClass, **metadata: Any
    ) -> ConsoleRenderableClass:
        style = self

        class Decorated(klass):  # type: ignore[valid-type,misc]
            def __rich_console__(
                self, console: Console, options: ConsoleOptions
            ) -> RenderResult:
                lines = Segment.split_lines(super().__rich_console__(console, options))  # type: ignore

                yield from style.decorate(lines=lines, console=console, **metadata)

        return Decorated  # type: ignore

    def decorate_progress_log_line(
        self, line: str, index: int, max_lines: int = -1, total_lines: int = -1
    ) -> str:
        if max_lines == -1:
            return line

        # Adjust minimum brightness based on number of lines
        # Fewer lines = higher minimum brightness
        min_brightness = max(0.4, 1.0 - (total_lines / max_lines) * 0.6)
        brightness_range = 1.0 - min_brightness

        # Calculate brightness based on position in the sequence
        brightness_pct = (index / total_lines) * brightness_range + min_brightness

        # Apply brightness to RGB values
        r = g = b = int(255 * brightness_pct)

        color = f"#{r:02x}{g:02x}{b:02x}"

        return f"[{color}]" + line

    @abstractmethod
    def decorate(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animation_status: ANIMATION_STATUS = "no_animation",
        **kwargs: Any,
    ) -> Generator[Segment, None, None]:
        raise NotImplementedError()

    def _get_animation_colors(
        self,
        console: Console,
        steps: int = 5,
        animation_status: ANIMATION_STATUS = "started",
        **metadata: Any,
    ) -> List[Color]:
        animated = animation_status == "started"

        if animation_status == "error":
            base_color = console.get_style("error").color

            if base_color is None:
                base_color = Color.parse("red")

        else:
            base_color = console.get_style("progress").bgcolor

        if not base_color:
            base_color = Color.parse("white")

        if animated and base_color.triplet is not None:
            return [lighten(base_color, 0.1 * i) for i in range(0, steps)]

        return [base_color] * steps
