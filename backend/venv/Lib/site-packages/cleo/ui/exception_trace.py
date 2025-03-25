from __future__ import annotations

import ast
import builtins
import inspect
import io
import keyword
import os
import re
import sys
import tokenize

from typing import TYPE_CHECKING
from typing import ClassVar

from crashtest.frame_collection import FrameCollection

from cleo.formatters.formatter import Formatter


if TYPE_CHECKING:
    from crashtest.frame import Frame
    from crashtest.solution_providers.solution_provider_repository import (
        SolutionProviderRepository,
    )

    from cleo.io.io import IO
    from cleo.io.outputs.output import Output


class Highlighter:
    TOKEN_DEFAULT = "token_default"
    TOKEN_COMMENT = "token_comment"
    TOKEN_STRING = "token_string"
    TOKEN_NUMBER = "token_number"
    TOKEN_KEYWORD = "token_keyword"
    TOKEN_BUILTIN = "token_builtin"
    TOKEN_OP = "token_op"
    LINE_MARKER = "line_marker"
    LINE_NUMBER = "line_number"

    DEFAULT_THEME: ClassVar[dict[str, str]] = {
        TOKEN_STRING: "fg=yellow;options=bold",
        TOKEN_NUMBER: "fg=blue;options=bold",
        TOKEN_COMMENT: "fg=default;options=dark,italic",
        TOKEN_KEYWORD: "fg=magenta;options=bold",
        TOKEN_BUILTIN: "fg=default;options=bold",
        TOKEN_DEFAULT: "fg=default",
        TOKEN_OP: "fg=default;options=dark",
        LINE_MARKER: "fg=red;options=bold",
        LINE_NUMBER: "fg=default;options=dark",
    }

    KEYWORDS: ClassVar[set[str]] = set(keyword.kwlist)
    BUILTINS: ClassVar[set[str]] = set(dir(builtins))

    UI: ClassVar[dict[bool, dict[str, str]]] = {
        False: {"arrow": ">", "delimiter": "|"},
        True: {"arrow": "→", "delimiter": "│"},
    }

    def __init__(self, supports_utf8: bool = True) -> None:
        self._theme = self.DEFAULT_THEME.copy()
        self._ui = self.UI[supports_utf8]

    def code_snippet(
        self, source: str, line: int, lines_before: int = 2, lines_after: int = 2
    ) -> list[str]:
        token_lines = self.highlighted_lines(source)
        token_lines = self.line_numbers(token_lines, line)

        offset = line - lines_before - 1
        offset = max(offset, 0)
        length = lines_after + lines_before + 1
        return token_lines[offset : offset + length]

    def highlighted_lines(self, source: str) -> list[str]:
        source = source.replace("\r\n", "\n").replace("\r", "\n")

        return self.split_to_lines(source)

    def split_to_lines(self, source: str) -> list[str]:
        lines = []
        current_line = 1
        current_col = 0
        buffer = ""
        current_type = None
        source_io = io.BytesIO(source.encode())
        formatter = Formatter()

        def readline() -> bytes:
            return formatter.format(
                formatter.escape(source_io.readline().decode())
            ).encode()

        tokens = tokenize.tokenize(readline)
        line = ""
        for token_info in tokens:
            token_type, token_string, start, end, _ = token_info
            lineno = start[0]
            if lineno == 0:
                # Encoding line
                continue

            if token_type == tokenize.ENDMARKER:
                # End of source
                if current_type is None:
                    current_type = self.TOKEN_DEFAULT

                line += f"<{self._theme[current_type]}>{buffer}</>"
                lines.append(line)
                break

            if lineno > current_line:
                if current_type is None:
                    current_type = self.TOKEN_DEFAULT

                diff = lineno - current_line
                if diff > 1:
                    lines += [""] * (diff - 1)

                stripped_buffer = buffer.rstrip("\n")
                line += f"<{self._theme[current_type]}>{stripped_buffer}</>"

                # New line
                lines.append(line)
                line = ""
                current_line = lineno
                current_col = 0
                buffer = ""

            if token_string in self.KEYWORDS:
                new_type = self.TOKEN_KEYWORD
            elif token_string in self.BUILTINS or token_string == "self":
                new_type = self.TOKEN_BUILTIN
            elif token_type == tokenize.STRING:
                new_type = self.TOKEN_STRING
            elif token_type == tokenize.NUMBER:
                new_type = self.TOKEN_NUMBER
            elif token_type == tokenize.COMMENT:
                new_type = self.TOKEN_COMMENT
            elif token_type == tokenize.OP:
                new_type = self.TOKEN_OP
            elif token_type == tokenize.NEWLINE:
                continue
            else:
                new_type = self.TOKEN_DEFAULT

            if current_type is None:
                current_type = new_type

            if start[1] > current_col:
                buffer += token_info.line[current_col : start[1]]

            if current_type != new_type:
                line += f"<{self._theme[current_type]}>{buffer}</>"
                buffer = ""
                current_type = new_type

            if lineno < end[0]:
                # The token spans multiple lines
                token_lines = token_string.split("\n")
                line += f"<{self._theme[current_type]}>{token_lines[0]}</>"
                lines.append(line)
                for token_line in token_lines[1:-1]:
                    lines.append(f"<{self._theme[current_type]}>{token_line}</>")

                current_line = end[0]
                buffer = token_lines[-1][: end[1]]
                line = ""
                continue

            buffer += token_string
            current_col = end[1]
            current_line = lineno

        return lines

    def line_numbers(self, lines: list[str], mark_line: int | None = None) -> list[str]:
        max_line_length = max(3, len(str(len(lines))))

        snippet_lines = []
        marker = f"<{self._theme[self.LINE_MARKER]}>{self._ui['arrow']}</> "
        no_marker = "  "
        for i, line in enumerate(lines):
            snippet = ""
            if mark_line is not None:
                snippet = marker if mark_line == i + 1 else no_marker

            line_number = f"{i + 1:>{max_line_length}}"
            styling = (
                "fg=default;options=bold"
                if mark_line == i + 1
                else self._theme[self.LINE_NUMBER]
            )
            snippet += (
                f"<{styling}>"
                f"{line_number}</><{self._theme[self.LINE_NUMBER]}>"
                f"{self._ui['delimiter']}</> {line}"
            )
            snippet_lines.append(snippet)

        return snippet_lines


class ExceptionTrace:
    """
    Renders the trace of an exception.
    """

    THEME: ClassVar[dict[str, str]] = {
        "comment": "<fg=black;options=bold>",
        "keyword": "<fg=yellow>",
        "builtin": "<fg=blue>",
        "literal": "<fg=magenta>",
    }

    AST_ELEMENTS: ClassVar[dict[str, list[str]]] = {
        "builtins": dir(builtins),
        "keywords": [
            getattr(ast, cls)
            for cls in dir(ast)
            if keyword.iskeyword(cls.lower())
            and inspect.isclass(getattr(ast, cls))
            and issubclass(getattr(ast, cls), ast.AST)
        ],
    }

    _FRAME_SNIPPET_CACHE: ClassVar[dict[tuple[Frame, int, int], list[str]]] = {}

    def __init__(
        self,
        exception: Exception,
        solution_provider_repository: SolutionProviderRepository | None = None,
    ) -> None:
        self._exception = exception
        self._solution_provider_repository = solution_provider_repository
        self._exc_info = sys.exc_info()
        self._ignore: str | None = None

    def ignore_files_in(self, ignore: str) -> ExceptionTrace:
        self._ignore = ignore

        return self

    def render(self, io: IO | Output, simple: bool = False) -> None:
        # If simple rendering wouldn't show anything useful, abandon it.
        simple_string = str(self._exception) if simple else ""
        if simple_string:
            io.write_line("")
            io.write_line(f"<error>{simple_string}</error>")
        else:
            self._render_exception(io, self._exception)

        self._render_solution(io, self._exception)

    def _render_exception(self, io: IO | Output, exception: BaseException) -> None:
        from crashtest.inspector import Inspector

        inspector = Inspector(exception)
        if not inspector.frames:
            return

        if inspector.has_previous_exception():
            assert inspector.previous_exception is not None  # make mypy happy
            self._render_exception(io, inspector.previous_exception)
            io.write_line("")
            io.write_line(
                "The following error occurred when trying to handle this error:"
            )
            io.write_line("")

        self._render_trace(io, inspector.frames)

        self._render_line(io, f"<error>{inspector.exception_name}</error>", True)
        io.write_line("")
        exception_message = (
            Formatter().format(inspector.exception_message).replace("\n", "\n  ")
        )
        self._render_line(io, f"<b>{exception_message}</b>")

        current_frame = inspector.frames[-1]
        self._render_snippet(io, current_frame)

    def _render_snippet(self, io: IO | Output, frame: Frame) -> None:
        self._render_line(
            io,
            f"at <fg=green>{self._get_relative_file_path(frame.filename)}</>"
            f":<b>{frame.lineno}</b> in <fg=cyan>{frame.function}</>",
            True,
        )

        code_lines = Highlighter(supports_utf8=io.supports_utf8()).code_snippet(
            frame.file_content, frame.lineno, 4, 4
        )

        for code_line in code_lines:
            self._render_line(io, code_line, indent=4)

    def _render_solution(self, io: IO | Output, exception: Exception) -> None:
        if self._solution_provider_repository is None:
            return

        solutions = self._solution_provider_repository.get_solutions_for_exception(
            exception
        )
        symbol = "•" if io.supports_utf8() else "*"

        for solution in solutions:
            title = solution.solution_title
            description = solution.solution_description
            links = solution.documentation_links

            description = description.replace("\n", "\n    ").strip(" ")

            joined_links = ",".join(f"\n    <fg=blue>{link}</>" for link in links)
            self._render_line(
                io,
                f"<fg=blue;options=bold>{symbol} </>"
                f"<fg=default;options=bold>{title.rstrip('.')}</>:"
                f" {description}{joined_links}",
                True,
            )

    def _render_trace(self, io: IO | Output, frames: FrameCollection) -> None:
        stack_frames = FrameCollection()
        for frame in frames:
            if (
                self._ignore
                and re.match(self._ignore, frame.filename)
                and not io.is_debug()
            ):
                continue

            stack_frames.append(frame)

        remaining_frames_length = len(stack_frames) - 1
        if io.is_very_verbose() and remaining_frames_length:
            self._render_line(io, "<fg=yellow>Stack trace</>:", True)
            max_frame_length = len(str(remaining_frames_length))
            frame_collections = stack_frames.compact()
            i = remaining_frames_length
            for collection in frame_collections:
                if collection.is_repeated():
                    if len(collection) > 1:
                        frames_message = f"<fg=yellow>{len(collection)}</> frames"
                    else:
                        frames_message = "frame"

                    self._render_line(
                        io,
                        f"<fg=blue>{'...':>{max_frame_length}}</>  "
                        f"Previous {frames_message} repeated "
                        f"<fg=blue>{collection.repetitions + 1}</> times",
                        True,
                    )

                    i -= len(collection) * (collection.repetitions + 1)

                for frame in collection:
                    relative_file_path = self._get_relative_file_path(frame.filename)
                    relative_file_path_parts = relative_file_path.split(os.path.sep)
                    relative_file_path = (
                        f"<fg=default;options=dark>{Formatter.escape(os.sep)}</>".join(
                            relative_file_path_parts[:-1]
                            + [
                                "<fg=default;options=bold>"
                                f"{relative_file_path_parts[-1]}</>"
                            ]
                        )
                    )
                    self._render_line(
                        io,
                        f"<fg=yellow>{i:>{max_frame_length}}</>  "
                        f"{relative_file_path}<fg=default;options=dark>:</>"
                        f"<b>{frame.lineno}</b> in <fg=cyan>{frame.function}</>",
                        True,
                    )

                    if io.is_debug():
                        if (frame, 2, 2) not in self._FRAME_SNIPPET_CACHE:
                            code_lines = Highlighter(
                                supports_utf8=io.supports_utf8()
                            ).code_snippet(
                                frame.file_content,
                                frame.lineno,
                            )

                            self._FRAME_SNIPPET_CACHE[(frame, 2, 2)] = code_lines

                        code_lines = self._FRAME_SNIPPET_CACHE[(frame, 2, 2)]

                        for code_line in code_lines:
                            self._render_line(
                                io,
                                f"{' ' * max_frame_length}{code_line}",
                                indent=3,
                            )
                    else:
                        highlighter = Highlighter(supports_utf8=io.supports_utf8())
                        try:
                            code_line = highlighter.highlighted_lines(
                                frame.line.strip()
                            )[0]
                        except tokenize.TokenError:
                            code_line = frame.line.strip()

                        self._render_line(
                            io, f"{' ' * (max_frame_length + 4)}{code_line}"
                        )

                    i -= 1

    def _render_line(
        self, io: IO | Output, line: str, new_line: bool = False, indent: int = 2
    ) -> None:
        if new_line:
            io.write_line("")

        io.write_line(f"{indent * ' '}{line}")

    def _get_relative_file_path(self, filepath: str) -> str:
        cwd = os.getcwd()

        if cwd:
            filepath = filepath.replace(cwd + os.path.sep, "")

        home = os.path.expanduser("~")
        if home:
            filepath = filepath.replace(home + os.path.sep, "~" + os.path.sep)

        return filepath
