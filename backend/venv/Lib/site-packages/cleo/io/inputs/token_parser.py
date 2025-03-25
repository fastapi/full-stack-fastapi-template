from __future__ import annotations


QUOTES = {"'", '"'}


class TokenParser:
    """
    Parses tokens from a string passed to StringArgs.
    """

    def __init__(self) -> None:
        self._string: str = ""
        self._cursor: int = 0
        self._current: str | None = None
        self._next_: str | None = None

    def parse(self, string: str) -> list[str]:
        self._string = string
        self._cursor = 0
        self._current = None
        if string:
            self._current = string[0]

        self._next_ = string[1] if len(string) > 1 else None

        return self._parse()

    def _parse(self) -> list[str]:
        tokens = []

        while self._current is not None:
            if self._current.isspace():
                # Skip spaces
                self._next()

                continue

            tokens.append(self._parse_token())

        return tokens

    def _next(self) -> None:
        """
        Advances the cursor to the next position.
        """
        if self._current is None:
            return

        self._cursor += 1
        self._current = self._next_

        if self._cursor + 1 < len(self._string):
            self._next_ = self._string[self._cursor + 1]
        else:
            self._next_ = None

    def _parse_token(self) -> str:
        token = ""

        while self._current is not None:
            if self._current.isspace():
                self._next()

                break

            if self._current == "\\":
                token += self._parse_escape_sequence()
            elif self._current in QUOTES:
                token += self._parse_quoted_string()
            else:
                token += self._current
                self._next()

        return token

    def _parse_quoted_string(self) -> str:
        string = ""
        delimiter = self._current

        # Skip first delimiter
        self._next()
        while self._current is not None:
            if self._current == delimiter:
                # Skip last delimiter
                self._next()

                break

            if self._current == "\\":
                string += self._parse_escape_sequence()
            elif self._current == '"':
                string += f'"{self._parse_quoted_string()}"'
            elif self._current == "'":
                string += f"'{self._parse_quoted_string()}'"
            else:
                string += self._current
                self._next()

        return string

    def _parse_escape_sequence(self) -> str:
        if self._next_ in QUOTES:
            sequence = self._next_
        else:
            assert self._next_ is not None
            sequence = "\\" + self._next_

        self._next()
        self._next()

        return sequence
