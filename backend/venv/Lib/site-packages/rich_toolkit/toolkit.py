from typing import Any, Dict, List, Union

from rich.console import Console, RenderableType
from rich.theme import Theme

from .styles.base import BaseStyle
from .input import Input
from .menu import Menu, Option, ReturnValue
from .progress import Progress


class RichToolkitTheme:
    def __init__(self, style: BaseStyle, theme: Dict[str, str]) -> None:
        self.style = style
        self.rich_theme = Theme(theme)


class RichToolkit:
    def __init__(
        self,
        theme: RichToolkitTheme,
        handle_keyboard_interrupts: bool = True,
    ) -> None:
        self.console = Console(theme=theme.rich_theme)
        self.theme = theme
        self.handle_keyboard_interrupts = handle_keyboard_interrupts

    def __enter__(self):
        self.console.print()
        return self

    def __exit__(
        self, exc_type: Any, exc_value: Any, traceback: Any
    ) -> Union[bool, None]:
        if self.handle_keyboard_interrupts and exc_type is KeyboardInterrupt:
            # we want to handle keyboard interrupts gracefully, instead of showing a traceback
            # or any other error message
            return True

        self.console.print()

    def print_title(self, title: str, **metadata: Any) -> None:
        self.console.print(
            self.theme.style.with_decoration(title, title=True, **metadata)
        )

    def print(self, *renderables: RenderableType, **metadata: Any) -> None:
        self.console.print(self.theme.style.with_decoration(*renderables, **metadata))

    def print_as_string(self, *renderables: RenderableType, **metadata: Any) -> str:
        with self.console.capture() as capture:
            self.print(*renderables, **metadata)

        return capture.get().rstrip()

    def print_line(self) -> None:
        self.console.print(self.theme.style.empty_line())

    def confirm(self, title: str, **metadata: Any) -> bool:
        return self.ask(
            title=title,
            options=[
                Option({"value": True, "name": "Yes"}),
                Option({"value": False, "name": "No"}),
            ],
            inline=True,
            **metadata,
        )

    def ask(
        self,
        title: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        allow_filtering: bool = False,
        **metadata: Any,
    ) -> ReturnValue:
        return Menu(
            title=title,
            options=options,
            console=self.console,
            style=self.theme.style,
            inline=inline,
            allow_filtering=allow_filtering,
            cursor_offset=self.theme.style.cursor_offset,
            **metadata,
        ).ask()

    def input(
        self, title: str, default: str = "", password: bool = False, **metadata: Any
    ) -> str:
        return Input(
            console=self.console,
            style=self.theme.style,
            title=title,
            default=default,
            cursor_offset=self.theme.style.cursor_offset,
            password=password,
            **metadata,
        ).ask()

    def progress(
        self,
        title: str,
        transient: bool = False,
        transient_on_error: bool = False,
        inline_logs: bool = False,
        lines_to_show: int = -1,
    ) -> Progress:
        return Progress(
            title=title,
            console=self.console,
            style=self.theme.style,
            transient=transient,
            transient_on_error=transient_on_error,
            inline_logs=inline_logs,
            lines_to_show=lines_to_show,
        )
