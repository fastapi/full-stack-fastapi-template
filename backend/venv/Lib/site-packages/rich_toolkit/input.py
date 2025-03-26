import string
from typing import Any, Optional, Tuple
from abc import ABC, abstractmethod

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.live_render import LiveRender

from rich_toolkit.styles.base import BaseStyle


class TextInputHandler:
    DOWN_KEY = "\x1b[B"
    UP_KEY = "\x1b[A"
    LEFT_KEY = "\x1b[D"
    RIGHT_KEY = "\x1b[C"
    BACKSPACE_KEY = "\x7f"
    DELETE_KEY = "\x1b[3~"

    def __init__(self, cursor_offset: int = 0):
        self.text = ""
        self.cursor_position = 0
        self._cursor_offset = cursor_offset

    def _move_cursor_left(self) -> None:
        self.cursor_position = max(0, self.cursor_position - 1)

    def _move_cursor_right(self) -> None:
        self.cursor_position = min(len(self.text), self.cursor_position + 1)

    def _insert_char(self, char: str) -> None:
        self.text = (
            self.text[: self.cursor_position] + char + self.text[self.cursor_position :]
        )
        self._move_cursor_right()

    def _delete_char(self) -> None:
        if self.cursor_position == 0:
            return

        self.text = (
            self.text[: self.cursor_position - 1] + self.text[self.cursor_position :]
        )
        self._move_cursor_left()

    def _delete_forward(self) -> None:
        if self.cursor_position == len(self.text):
            return

        self.text = (
            self.text[: self.cursor_position] + self.text[self.cursor_position + 1 :]
        )

    def update_text(self, text: str) -> None:
        if text == self.BACKSPACE_KEY:
            self._delete_char()
        elif text == self.DELETE_KEY:
            self._delete_forward()
        elif text == self.LEFT_KEY:
            self._move_cursor_left()
        elif text == self.RIGHT_KEY:
            self.cursor_position = min(len(self.text), self.cursor_position + 1)
        elif text in (self.UP_KEY, self.DOWN_KEY):
            pass
        else:
            for char in text:
                if char in string.printable:
                    self._insert_char(char)

    def fix_cursor(self) -> Tuple[Control, ...]:
        return (Control.move_to_column(self._cursor_offset + self.cursor_position),)


class LiveInput(ABC, TextInputHandler):
    def __init__(
        self,
        console: Console,
        style: Optional[BaseStyle] = None,
        cursor_offset: int = 0,
        **metadata: Any,
    ):
        self.console = console
        self._live_render = LiveRender("")

        if style is None:
            self._live_render = LiveRender("")
        else:
            self._live_render = style.decorate_class(LiveRender, **metadata)("")

        self._padding_bottom = 1

        super().__init__(cursor_offset=cursor_offset)

    @abstractmethod
    def render_result(self) -> RenderableType:
        raise NotImplementedError

    @abstractmethod
    def render_input(self) -> RenderableType:
        raise NotImplementedError

    @property
    def should_show_cursor(self) -> bool:
        return True

    def position_cursor(self) -> Tuple[Control, ...]:
        return (self._live_render.position_cursor(),)

    def _refresh(self, show_result: bool = False) -> None:
        renderable = self.render_result() if show_result else self.render_input()

        self._live_render.set_renderable(renderable)

        self._render(show_result)

    def _render(self, show_result: bool = False) -> None:
        after = self.fix_cursor() if not show_result else ()

        self.console.print(
            Control.show_cursor(self.should_show_cursor),
            *self.position_cursor(),
            self._live_render,
            *after,
        )


class Input(LiveInput):
    def __init__(
        self,
        console: Console,
        title: str,
        style: Optional[BaseStyle] = None,
        default: str = "",
        cursor_offset: int = 0,
        password: bool = False,
        **metadata: Any,
    ):
        self.title = title
        self.default = default
        self.password = password

        self.console = console
        self.style = style

        super().__init__(
            console=console, style=style, cursor_offset=cursor_offset, **metadata
        )

    def render_result(self) -> RenderableType:
        if self.password:
            return self.title

        return self.title + " [result]" + (self.text or self.default)

    def render_input(self) -> Group:
        text = self.text

        if self.password:
            text = "*" * len(self.text)

        # if there's no default value, add a space to keep the cursor visible
        # and, most importantly, in the right place
        default = self.default or " "

        text = f"[text]{text}[/]" if self.text else f"[placeholder]{default }[/]"

        return Group(self.title, text)

    def ask(self) -> str:
        self._refresh()

        while True:
            try:
                key = click.getchar()

                if key == "\r":
                    break

                self.update_text(key)

            except KeyboardInterrupt:
                exit()

            self._refresh()

        self._refresh(show_result=True)

        for _ in range(self._padding_bottom):
            self.console.print()

        return self.text or self.default
