from __future__ import annotations

import re

from typing import ClassVar

from cleo.exceptions import CleoValueError
from cleo.formatters.style import Style
from cleo.formatters.style_stack import StyleStack


class Formatter:
    TAG_REGEX = re.compile(r"(?ix)<(([a-z](?:[^<>]*)) | /([a-z](?:[^<>]*))?)>")

    _inline_styles_cache: ClassVar[dict[str, Style]] = {}

    def __init__(
        self, decorated: bool = False, styles: dict[str, Style] | None = None
    ) -> None:
        self._decorated = decorated
        self._styles: dict[str, Style] = {}

        self.set_style("error", Style("red", options=["bold"]))
        self.set_style("info", Style("blue"))
        self.set_style("comment", Style("green"))
        self.set_style("question", Style("cyan"))
        self.set_style("c1", Style("cyan"))
        self.set_style("c2", Style("default", options=["bold"]))
        self.set_style("b", Style("default", options=["bold"]))

        for name, style in (styles or {}).items():
            self.set_style(name, style)

        self._style_stack = StyleStack()

    @classmethod
    def escape(cls, text: str) -> str:
        """
        Escapes "<" special char in given text.
        """
        text = re.sub(r"([^\\]?)<", "\\1\\<", text)

        return cls.escape_trailing_backslash(text)

    @staticmethod
    def escape_trailing_backslash(text: str) -> str:
        """
        Escapes trailing "\\" in given text.
        """
        if text.endswith("\\"):
            length = len(text)
            text = text.rstrip("\\").replace("\0", "").ljust(length, "\0")

        return text

    def decorated(self, decorated: bool = True) -> None:
        self._decorated = decorated

    def is_decorated(self) -> bool:
        return self._decorated

    def set_style(self, name: str, style: Style) -> None:
        self._styles[name] = style

    def has_style(self, name: str) -> bool:
        return name in self._styles

    def style(self, name: str) -> Style:
        if not self.has_style(name):
            raise CleoValueError(f'Undefined style: "{name}"')

        return self._styles[name]

    def format(self, message: str) -> str:
        return self.format_and_wrap(message, 0)

    def format_and_wrap(self, message: str, width: int) -> str:
        offset = 0
        output = ""
        current_line_length = 0
        for match in self.TAG_REGEX.finditer(message):
            pos = match.start()
            text = match.group(0)

            if pos != 0 and message[pos - 1] == "\\":
                continue

            # add the text up to the next tag
            formatted, current_line_length = self._apply_current_style(
                message[offset:pos], output, width, current_line_length
            )
            output += formatted
            offset = pos + len(text)

            # Opening tag
            seen_open = text[1] != "/"
            tag = match.group(1) if seen_open else match.group(2)

            style = None
            if tag:
                style = self._create_style_from_string(tag)

            if not (seen_open or tag):
                # </>
                self._style_stack.pop()
            elif style is None:
                formatted, current_line_length = self._apply_current_style(
                    text, output, width, current_line_length
                )
                output += formatted
            elif seen_open:
                self._style_stack.push(style)
            else:
                self._style_stack.pop(style)

        formatted, current_line_length = self._apply_current_style(
            message[offset:], output, width, current_line_length
        )
        output += formatted
        return output.replace("\0", "\\").replace("\\<", "<")

    def remove_format(self, text: str) -> str:
        decorated = self._decorated

        self._decorated = False
        text = re.sub(r"\033\[[^m]*m", "", self.format(text))

        self._decorated = decorated

        return text

    def _create_style_from_string(self, string: str) -> Style | None:
        if string in self._styles:
            return self._styles[string]

        if string in self._inline_styles_cache:
            return self._inline_styles_cache[string]

        matches = re.findall(r"([^=]+)=([^;]+)(;|$)", string.lower())
        if not matches:
            return None

        style = Style()

        for where, style_options, _ in matches:
            if where == "fg":
                style.foreground(style_options)
            elif where == "bg":
                style.background(style_options)
            else:
                try:
                    for option in map(str.strip, style_options.split(",")):
                        style.set_option(option)
                except ValueError:
                    return None

        self._inline_styles_cache[string] = style

        return style

    def _apply_current_style(
        self, text: str, current: str, width: int, current_line_length: int
    ) -> tuple[str, int]:
        if not text:
            return "", current_line_length

        if not width:
            if self.is_decorated():
                return self._style_stack.current.apply(text), current_line_length

            return text, current_line_length

        if not current_line_length and current:
            text = text.lstrip()

        if current_line_length:
            i = width - current_line_length
            prefix = text[:i] + "\n"
            text = text[i:]
        else:
            prefix = ""

        m = re.match(r"(\n)$", text)
        text = prefix + re.sub(rf"([^\n]{{{width}}})\ *", "\\1\n", text)
        text = text.rstrip("\n") + (m.group(1) if m else "")

        if not current_line_length and current and not current.endswith("\n"):
            text = "\n" + text

        lines = text.split("\n")
        for line in lines:
            current_line_length += len(line)
            if current_line_length >= width:
                current_line_length = 0

        if self.is_decorated():
            apply = self._style_stack.current.apply
            text = "\n".join(map(apply, lines))

        return text, current_line_length
