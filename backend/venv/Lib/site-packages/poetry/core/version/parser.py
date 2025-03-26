from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from pathlib import Path

    from lark import Lark
    from lark import Tree


class Parser:
    def __init__(
        self, grammar: Path, parser: str = "lalr", debug: bool = False
    ) -> None:
        self._grammar = grammar
        self._parser = parser
        self._debug = debug
        self._lark: Lark | None = None

    def parse(self, text: str, **kwargs: Any) -> Tree:
        from lark import Lark

        if self._lark is None:
            self._lark = Lark.open(
                grammar_filename=self._grammar, parser=self._parser, debug=self._debug
            )

        return self._lark.parse(text=text, **kwargs)
