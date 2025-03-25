from __future__ import annotations

import math
import re
import time

from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Match

from cleo._utils import format_time
from cleo.cursor import Cursor
from cleo.io.io import IO
from cleo.io.outputs.section_output import SectionOutput
from cleo.terminal import Terminal
from cleo.ui.component import Component


if TYPE_CHECKING:
    from cleo.io.outputs.output import Output


class ProgressBar(Component):
    """
    The ProgressBar provides helpers to display progress output.
    """

    name = "progress_bar"

    # Options
    bar_width = 28
    bar_char = None
    empty_bar_char = "-"
    progress_char = ">"
    redraw_freq: int | None = 1

    formats: ClassVar[dict[str, str]] = {
        "normal": " %current%/%max% [%bar%] %percent:3s%%",
        "normal_nomax": " %current% [%bar%]",
        "verbose": " %current%/%max% [%bar%] %percent:3s%% %elapsed:-6s%",
        "verbose_nomax": " %current% [%bar%] %elapsed:6s%",
        "very_verbose": (
            " %current%/%max% [%bar%] %percent:3s%%" " %elapsed:6s%/%estimated:-6s%"
        ),
        "very_verbose_nomax": " %current% [%bar%] %elapsed:6s%",
        "debug": " %current%/%max% [%bar%] %percent:3s%% %elapsed:6s%/%estimated:-6s%",
        "debug_nomax": " %current% [%bar%] %elapsed:6s%",
    }

    def __init__(
        self,
        io: IO | Output,
        max: int = 0,
        min_seconds_between_redraws: float = 0.1,
    ) -> None:
        # If we have an IO, ensure we write to the error output
        if isinstance(io, IO):
            io = io.error_output

        self._io = io
        self._terminal = Terminal().size
        self._max = 0
        self._step_width: int = 1
        self._set_max_steps(max)
        self._step = 0
        self._percent = 0.0
        self._format: str | None = None
        self._internal_format: str | None = None
        self._format_line_count = 0
        self._previous_message: str | None = None
        self._should_overwrite = True
        self._min_seconds_between_redraws = 0.0
        self._max_seconds_between_redraws = 1.0
        self._write_count = 0

        if min_seconds_between_redraws > 0:
            self.redraw_freq = None
            self._min_seconds_between_redraws = min_seconds_between_redraws

        if not self._io.formatter.is_decorated():
            # Disable overwrite when output does not support ANSI codes.
            self._should_overwrite = False

            # Set a reasonable redraw frequency so output isn't flooded
            self.redraw_freq = None

        self._messages: dict[str, str] = {}

        self._start_time = time.time()
        self._last_write_time = 0.0
        self._cursor = Cursor(self._io)

    def set_message(self, message: str, name: str = "message") -> None:
        self._messages[name] = message

    def get_message(self, name: str = "message") -> str:
        return self._messages[name]

    def get_start_time(self) -> float:
        return self._start_time

    def get_max_steps(self) -> int:
        return self._max

    def get_progress(self) -> int:
        return self._step

    def get_progress_percent(self) -> float:
        return self._percent

    def set_bar_character(self, character: str) -> ProgressBar:
        self.bar_char = character

        return self

    def get_bar_character(self) -> str:
        if self.bar_char is None:
            if self._max:
                return "="

            return self.empty_bar_char

        return self.bar_char

    def set_bar_width(self, width: int) -> ProgressBar:
        self.bar_width = width

        return self

    def get_empty_bar_character(self) -> str:
        return self.empty_bar_char

    def set_empty_bar_character(self, character: str) -> ProgressBar:
        self.empty_bar_char = character

        return self

    def get_progress_character(self) -> str:
        return self.progress_char

    def set_progress_character(self, character: str) -> ProgressBar:
        self.progress_char = character

        return self

    def set_format(self, fmt: str) -> None:
        self._format = None
        self._internal_format = fmt

    def set_redraw_frequency(self, freq: int) -> None:
        if self.redraw_freq is not None:
            self.redraw_freq = max(freq, 1)

    def min_seconds_between_redraws(self, freq: float) -> None:
        if freq > 0:
            self.redraw_freq = None
            self._min_seconds_between_redraws = freq

    def max_seconds_between_redraws(self, freq: float) -> None:
        self._max_seconds_between_redraws = freq

    def start(self, max: int | None = None) -> None:
        """
        Start the progress output.
        """
        self._start_time = time.time()
        self._step = 0
        self._percent = 0.0

        if max is not None:
            self._set_max_steps(max)

        self.display()

    def advance(self, step: int = 1) -> None:
        """
        Advances the progress output X steps.
        """
        self.set_progress(self._step + step)

    def set_progress(self, step: int) -> None:
        """
        Sets the current progress.
        """
        if self._max and step > self._max:
            self._max = step
        elif step < 0:
            step = 0

        redraw_freq = (
            (self._max or 10) / 10 if self.redraw_freq is None else self.redraw_freq
        )
        prev_period = int(self._step / redraw_freq)
        curr_period = int(step / redraw_freq)

        self._step = step
        self._percent = step / (self._max or math.inf)

        time_interval = time.time() - self._last_write_time

        # Draw regardless of other limits
        if step == self._max:
            self.display()

            return

        # Throttling
        if time_interval < self._min_seconds_between_redraws:
            return

        # Draw each step period, but not too late
        if (
            prev_period != curr_period
            or time_interval >= self._max_seconds_between_redraws
        ):
            self.display()

    def finish(self) -> None:
        """
        Finish the progress output.
        """
        if not self._max:
            self._max = self._step

        if self._step == self._max and not self._should_overwrite:
            return

        self.set_progress(self._max)

    def display(self) -> None:
        """
        Output the current progress string.
        """
        if self._io.is_quiet():
            return

        if self._format is None:
            self._set_real_format(
                self._internal_format or self._determine_best_format()
            )

        self._overwrite(self._build_line())

    def _overwrite_callback(self, matches: Match[str]) -> str:
        if hasattr(self, f"_formatter_{matches.group(1)}"):
            text = str(getattr(self, f"_formatter_{matches.group(1)}")())
        elif matches.group(1) in self._messages:
            text = self._messages[matches.group(1)]
        else:
            return matches.group(0)

        if matches.group(2):
            n = int(matches.group(2).lstrip("-").rstrip("s"))
            if matches.group(2).startswith("-"):
                return text.ljust(n)
            return text.rjust(n)

        return text

    def clear(self) -> None:
        """
        Removes the progress bar from the current line.

        This is useful if you wish to write some output
        while a progress bar is running.
        Call display() to show the progress bar again.
        """
        if not self._should_overwrite:
            return

        if self._format is None:
            self._set_real_format(
                self._internal_format or self._determine_best_format()
            )

        self._overwrite("\n" * self._format_line_count)

    def _set_real_format(self, fmt: str) -> None:
        """
        Sets the progress bar format.
        """
        # try to use the _nomax variant if available
        if not self._max and fmt + "_nomax" in self.formats:
            self._format = self.formats[fmt + "_nomax"]
        else:
            self._format = self.formats.get(fmt, fmt)
        assert self._format is not None
        self._format_line_count = self._format.count("\n")

    def _set_max_steps(self, mx: int) -> None:
        """
        Sets the progress bar maximal steps.
        """
        self._max = max(0, mx)
        self._step_width = len(str(self._max)) if self._max else 4

    def _overwrite(self, message: str) -> None:
        """
        Overwrites a previous message to the output.
        """
        if self._previous_message == message:
            return

        original_message = message

        if self._should_overwrite:
            if self._previous_message is not None:
                if isinstance(self._io, SectionOutput):
                    lines_to_clear = (
                        len(self._io.remove_format(message)) // self._terminal.width
                        + self._format_line_count
                        + 1
                    )
                    self._io.clear(lines_to_clear)
                else:
                    if self._format_line_count:
                        self._cursor.move_up(self._format_line_count)

                    self._cursor.move_to_column(1)
                    self._cursor.clear_line()
        elif self._step > 0:
            message = "\n" + message

        self._previous_message = original_message
        self._last_write_time = time.time()

        self._io.write(message)
        self._write_count += 1

    def _determine_best_format(self) -> str:
        fmt = "normal"
        if self._io.is_debug():
            fmt = "debug"
        elif self._io.is_very_verbose():
            fmt = "very_verbose"
        elif self._io.is_verbose():
            fmt = "verbose"

        return fmt if self._max else f"{fmt}_nomax"

    @property
    def bar_offset(self) -> int:
        if self._max:
            return math.floor(self._percent * self.bar_width)
        if self.redraw_freq is None:
            return math.floor(
                (min(5, self.bar_width // 15) * self._write_count) % self.bar_width
            )
        return math.floor(self._step % self.bar_width)

    def _formatter_bar(self) -> str:
        complete_bars = self.bar_offset

        display = self.get_bar_character() * int(complete_bars)

        if complete_bars < self.bar_width:
            empty_bars = (
                self.bar_width
                - complete_bars
                - len(self._io.remove_format(self.progress_char))
            )
            display += self.progress_char + self.empty_bar_char * int(empty_bars)

        return display

    def _formatter_elapsed(self) -> str:
        return format_time(time.time() - self._start_time)

    def _formatter_remaining(self) -> str:
        if not self._max:
            raise RuntimeError(
                "Unable to display the remaining time "
                "if the maximum number of steps is not set."
            )

        if not self._step:
            remaining = 0
        else:
            remaining = round(
                (time.time() - self._start_time) / self._step * (self._max - self._max)
            )

        return format_time(remaining)

    def _formatter_estimated(self) -> int:
        if not self._max:
            raise RuntimeError(
                "Unable to display the estimated time "
                "if the maximum number of steps is not set."
            )

        if not self._step:
            return 0

        return round((time.time() - self._start_time) / self._step * self._max)

    def _formatter_current(self) -> str:
        return str(self._step).rjust(self._step_width)

    def _formatter_max(self) -> int:
        return self._max

    def _formatter_percent(self) -> int:
        return int(math.floor(self._percent * 100))

    def _build_line(self) -> str:
        regex = re.compile(r"(?i)%([a-z\-_]+)(?::([^%]+))?%")
        assert self._format is not None
        line = regex.sub(self._overwrite_callback, self._format)

        # gets string length for each sub line with multiline format
        lines_length = [
            len(self._io.remove_format(sub_line.rstrip("\r")))
            for sub_line in line.split("\n")
        ]

        lines_width = max(lines_length)

        terminal_width = self._terminal.width

        if lines_width <= terminal_width:
            return line

        self.set_bar_width(self.bar_width - lines_width + terminal_width)

        return regex.sub(self._overwrite_callback, self._format)
