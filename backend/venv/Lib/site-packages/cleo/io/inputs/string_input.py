from __future__ import annotations

from cleo.io.inputs.argv_input import ArgvInput
from cleo.io.inputs.token_parser import TokenParser


class StringInput(ArgvInput):
    """
    Represents an input provided as a string
    """

    def __init__(self, input: str) -> None:
        super().__init__([])

        self._set_tokens(self._tokenize(input))

    def _tokenize(self, input: str) -> list[str]:
        return TokenParser().parse(input)
