from typing import List, Optional

from rich.console import Console
from rich.live import Live
from typing_extensions import Any, Literal

from .styles.base import BaseStyle


class Progress(Live):
    def __init__(
        self,
        title: str,
        style: Optional[BaseStyle] = None,
        console: Optional[Console] = None,
        transient: bool = False,
        transient_on_error: bool = False,
        inline_logs: bool = False,
        lines_to_show: int = -1,
    ) -> None:
        self.current_message = title
        self.style = style
        self.is_error = False
        self._transient_on_error = transient_on_error
        self._inline_logs = inline_logs
        self._lines_to_show = lines_to_show

        self.logs: List[str] = []

        super().__init__(console=console, refresh_per_second=8, transient=transient)

    # TODO: remove this once rich uses "Self"
    def __enter__(self) -> "Progress":
        self.start(refresh=self._renderable is not None)

        return self

    def get_renderable(self) -> Any:
        current_message = self.current_message

        if not self.style:
            return current_message

        animation_status: Literal["started", "stopped", "error"] = (
            "started" if self._started else "stopped"
        )

        if self.is_error:
            animation_status = "error"

        content = current_message

        if self._inline_logs:
            lines_to_show = (
                self.logs[-self._lines_to_show :]
                if self._lines_to_show > 0
                else self.logs
            )

            content = "\n".join(
                [
                    self.style.decorate_progress_log_line(
                        line,
                        index=index,
                        max_lines=self._lines_to_show,
                        total_lines=len(lines_to_show),
                    )
                    for index, line in enumerate(lines_to_show)
                ]
            )

        return self.style.with_decoration(
            content,
            animation_status=animation_status,
        )

    def log(self, text: str) -> None:
        if self._inline_logs:
            self.logs.append(text)
        else:
            self.current_message = text

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.is_error = True
        self.transient = self._transient_on_error
