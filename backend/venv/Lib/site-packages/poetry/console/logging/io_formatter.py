from __future__ import annotations

import logging
import sys
import textwrap

from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

from poetry.console.logging.filters import POETRY_FILTER
from poetry.console.logging.formatters import FORMATTERS


if TYPE_CHECKING:
    from logging import LogRecord


class IOFormatter(logging.Formatter):
    _colors: ClassVar[dict[str, str]] = {
        "error": "fg=red",
        "warning": "fg=yellow",
        "debug": "debug",
        "info": "fg=blue",
    }

    def format(self, record: LogRecord) -> str:
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.msg

            if record.name in FORMATTERS:
                msg = FORMATTERS[record.name].format(msg)
            elif level in self._colors:
                msg = f"<{self._colors[level]}>{msg}</>"

            record.msg = msg

        formatted = super().format(record)

        if not POETRY_FILTER.filter(record):
            # prefix all lines from third-party packages for easier debugging
            formatted = textwrap.indent(
                formatted, f"[{_log_prefix(record)}] ", lambda line: True
            )

        return formatted


def _log_prefix(record: LogRecord) -> str:
    prefix = _path_to_package(Path(record.pathname)) or record.module
    if record.name != "root":
        prefix = ":".join([prefix, record.name])
    return prefix


def _path_to_package(path: Path) -> str | None:
    """Return main package name from the LogRecord.pathname."""
    prefix: Path | None = None
    # Find the most specific prefix in sys.path.
    # We have to search the entire sys.path because a subsequent path might be
    # a sub path of the first match and thereby a better match.
    for syspath in sys.path:
        if (
            prefix and prefix in (p := Path(syspath)).parents and p in path.parents
        ) or (not prefix and (p := Path(syspath)) in path.parents):
            prefix = p
    if not prefix:
        # this is unexpected, but let's play it safe
        return None
    path = path.relative_to(prefix)
    return path.parts[0]  # main package name
