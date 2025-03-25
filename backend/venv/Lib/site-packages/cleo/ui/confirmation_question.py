from __future__ import annotations

import re

from typing import TYPE_CHECKING

from cleo.ui.question import Question


if TYPE_CHECKING:
    from cleo.io.io import IO


class ConfirmationQuestion(Question):
    """
    Represents a yes/no question.
    """

    def __init__(
        self, question: str, default: bool = True, true_answer_regex: str = r"(?i)^y"
    ) -> None:
        super().__init__(question, default)

        self._true_answer_regex = true_answer_regex
        self._normalizer = self._default_normalizer

    def _write_prompt(self, io: IO) -> None:
        message = (
            f"<question>{self._question} (yes/no)</> "
            f'[<comment>{"yes" if self._default else "no"}</>] '
        )

        io.write_error(message)

    def _default_normalizer(self, answer: str) -> bool:
        """
        Default answer normalizer.
        """
        if isinstance(answer, bool):
            return answer

        answer_is_true = re.match(self._true_answer_regex, answer) is not None
        if self.default is False:
            return bool(answer and answer_is_true)

        return not answer or answer_is_true
