from __future__ import annotations

import getpass
import os
import subprocess

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

from cleo.formatters.style import Style
from cleo.io.outputs.stream_output import StreamOutput


if TYPE_CHECKING:
    from cleo.io.io import IO

Validator = Callable[[str], Any]
Normalizer = Callable[[str], Any]


class Question:
    """
    A question that will be asked in a Console.
    """

    def __init__(self, question: str, default: Any = None) -> None:
        self._question = question
        self._default = default

        self._attempts: int | None = None
        self._hidden = False
        self._hidden_fallback = True
        self._autocomplete_values: list[str] = []
        self._validator: Validator = lambda s: s
        self._normalizer: Normalizer = lambda s: s
        self._error_message = 'Value "{}" is invalid'

    @property
    def question(self) -> str:
        return self._question

    @property
    def default(self) -> Any:
        return self._default

    @property
    def autocomplete_values(self) -> list[str]:
        return self._autocomplete_values

    @property
    def max_attempts(self) -> int | None:
        return self._attempts

    def is_hidden(self) -> bool:
        return self._hidden

    def hide(self, hidden: bool = True) -> None:
        if hidden is True and self._autocomplete_values:
            raise RuntimeError("A hidden question cannot use the autocompleter.")

        self._hidden = hidden

    def set_autocomplete_values(self, autocomplete_values: list[str]) -> None:
        if self.is_hidden():
            raise RuntimeError("A hidden question cannot use the autocompleter.")

        self._autocomplete_values = autocomplete_values

    def set_max_attempts(self, attempts: int | None) -> None:
        self._attempts = attempts

    def set_validator(self, validator: Validator) -> None:
        self._validator = validator

    def ask(self, io: IO) -> Any:
        """
        Asks the question to the user.
        """
        if not io.is_interactive():
            return self.default
        return self._validate_attempts(lambda: self._do_ask(io), io)

    def _do_ask(self, io: IO) -> Any:
        """
        Asks the question to the user.
        """
        self._write_prompt(io)

        if not (self._autocomplete_values and self._has_stty_available()):
            ret: str | None = None

            if self.is_hidden():
                try:
                    ret = self._get_hidden_response(io)
                except RuntimeError:
                    if not self._hidden_fallback:
                        raise

            if not ret:
                ret = self._read_from_input(io)
        else:
            ret = self._autocomplete(io)

        if len(ret) <= 0:
            ret = self._default

        return self._normalizer(ret)  # type: ignore[arg-type]

    def _write_prompt(self, io: IO) -> None:
        """
        Outputs the question prompt.
        """
        io.write_error(f"<question>{self._question}</question> ")

    def _write_error(self, io: IO, error: Exception) -> None:
        """
        Outputs an error message.
        """
        io.write_error_line(f"<error>{error!s}</error>")

    def _autocomplete(self, io: IO) -> str:
        """
        Autocomplete a question.
        """
        autocomplete = self._autocomplete_values

        ret = ""

        i = 0
        ofs = -1
        matches = list(autocomplete)
        num_matches = len(matches)

        # Add highlighted text style
        style = Style(options=["reverse"])
        io.error_output.formatter.set_style("hl", style)

        stty_mode = subprocess.check_output(["stty", "-g"]).decode().rstrip("\n")

        # Disable icanon (so we can read each keypress) and
        # echo (we'll do echoing here instead)
        subprocess.check_output(["stty", "-icanon", "-echo"])
        try:
            # Read a keypress
            while True:
                c = io.read(1)

                # Backspace character
                if c == "\177":
                    if num_matches == 0 and i != 0:
                        i -= 1
                        # Move cursor backwards
                        io.write_error("\033[1D")

                    if i == 0:
                        ofs = -1
                        matches = list(autocomplete)
                        num_matches = len(matches)
                    else:
                        num_matches = 0

                    # Pop the last character off the end of our string
                    ret = ret[:i]
                # Did we read an escape sequence
                elif c == "\033":
                    c += io.read(2)

                    # A = Up Arrow. B = Down Arrow
                    if c[2] == "A" or c[2] == "B":
                        if c[2] == "A" and ofs == -1:
                            ofs = 0

                        if num_matches == 0:
                            continue

                        ofs += -1 if c[2] == "A" else 1
                        ofs = (num_matches + ofs) % num_matches
                elif ord(c) < 32:
                    if c in ["\t", "\n"]:
                        if num_matches > 0 and ofs != -1:
                            ret = matches[ofs]
                            # Echo out remaining chars for current match
                            io.write_error(ret[i:])
                            i = len(ret)

                        if c == "\n":
                            io.write_error(c)
                            break

                        num_matches = 0

                    continue
                else:
                    io.write_error(c)
                    ret += c
                    i += 1

                    num_matches = 0
                    ofs = 0

                    for value in autocomplete:
                        # If typed characters match the beginning
                        # chunk of value (e.g. [AcmeDe]moBundle)
                        if value.startswith(ret) and i != len(value):
                            num_matches += 1
                            matches[num_matches - 1] = value

                # Erase characters from cursor to end of line
                io.write_error("\033[K")

                if num_matches > 0 and ofs != -1:
                    # Save cursor position
                    io.write_error("\0337")
                    # Write highlighted text
                    io.write_error("<hl>" + matches[ofs][i:] + "</hl>")
                    # Restore cursor position
                    io.write_error("\0338")
        finally:
            subprocess.call(["stty", f"{stty_mode}"])

        return ret

    def _get_hidden_response(self, io: IO) -> str:
        """
        Gets a hidden response from user.
        """
        stream = None
        if isinstance(io.error_output, StreamOutput):
            stream = io.error_output.stream
        return getpass.getpass("", stream=stream)

    def _validate_attempts(self, interviewer: Callable[[], Any], io: IO) -> Any:
        """
        Validates an attempt.
        """
        error = None
        attempts = self._attempts

        while attempts is None or attempts:
            if error is not None:
                self._write_error(io, error)

            try:
                return self._validator(interviewer())
            except Exception as e:
                error = e

            if attempts is not None:
                attempts -= 1

        assert error
        raise error

    def _read_from_input(self, io: IO) -> str:
        """
        Read user input.
        """
        ret = io.read_line(4096)

        if not ret:
            raise RuntimeError("Aborted")

        return ret.strip()

    def _has_stty_available(self) -> bool:
        with Path(os.devnull).open("w") as devnull:
            try:
                exit_code = subprocess.call(["stty"], stdout=devnull, stderr=devnull)
            except Exception:
                exit_code = 2

        return exit_code == 0
