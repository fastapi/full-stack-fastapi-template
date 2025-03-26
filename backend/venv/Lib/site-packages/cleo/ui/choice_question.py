from __future__ import annotations

import re

from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from cleo.exceptions import CleoValueError
from cleo.ui.question import Question


if TYPE_CHECKING:
    from cleo.io.io import IO


class SelectChoiceValidator:
    def __init__(self, question: ChoiceQuestion) -> None:
        """
        Constructor.
        """
        self._question = question
        self._values = question.choices

    def validate(self, selected: Any) -> str | list[str] | None:
        """
        Validate a choice.
        """
        # Collapse all spaces.
        if isinstance(selected, int):
            selected = str(selected)

        if selected is None:
            return None

        if self._question.supports_multiple_choices():
            # Check for a separated comma values
            _selected = selected.replace(" ", "")
            if not re.match(r"^[a-zA-Z0-9_-]+(?:,[a-zA-Z0-9_-]+)*$", _selected):
                raise CleoValueError(self._question.error_message.format(selected))

            selected_choices = _selected.split(",")
        else:
            selected_choices = [selected]

        multiselect_choices = []
        for value in selected_choices:
            results = []

            for key, choice in enumerate(self._values):
                if choice == value:
                    results.append(key)

            if len(results) > 1:
                raise CleoValueError(
                    "The provided answer is ambiguous. "
                    f"Value should be one of {' or '.join(str(r) for r in results)}."
                )

            if value in self._values:
                result = value
            elif value.isdigit() and 0 <= int(value) < len(self._values):
                result = self._values[int(value)]
            else:
                raise CleoValueError(self._question.error_message.format(value))

            multiselect_choices.append(result)

        if self._question.supports_multiple_choices():
            return multiselect_choices

        return cast("str | list[str] | None", multiselect_choices[0])


class ChoiceQuestion(Question):
    """
    Multiple choice question.
    """

    def __init__(
        self, question: str, choices: list[str], default: Any | None = None
    ) -> None:
        super().__init__(question, default)

        self._multi_select = False
        self._choices = choices
        self._validator = SelectChoiceValidator(self).validate
        self._autocomplete_values = choices
        self._prompt = " > "
        self._error_message = 'Value "{}" is invalid'

    @property
    def error_message(self) -> str:
        return self._error_message

    @property
    def choices(self) -> list[str]:
        return self._choices

    def supports_multiple_choices(self) -> bool:
        return self._multi_select

    def set_multi_select(self, multi_select: bool) -> None:
        self._multi_select = multi_select

    def set_error_message(self, message: str) -> None:
        self._error_message = message

    def _write_prompt(self, io: IO) -> None:
        """
        Outputs the question prompt.
        """
        message = self._question
        default = self._default

        if default is None:
            message = f"<question>{message}</question>: "
        elif self._multi_select:
            choices = self._choices
            default = default.split(",")

            for i, value in enumerate(default):
                default[i] = choices[int(value.strip())]

            message = (
                f"<question>{message}</question> "
                f"[<comment>{', '.join(default)}</comment>]:"
            )
        else:
            choices = self._choices
            message = (
                f"<question>{message}</question> "
                f"[<comment>{choices[int(default)]}</comment>]:"
            )

        width = len(str(len(self._choices) - 1)) if len(self._choices) > 1 else 1

        messages = [message]
        for key, value in enumerate(self._choices):
            messages.append(f" [<comment>{key: {width}}</>] {value}")

        io.write_error_line("\n".join(messages))

        message = self._prompt

        io.write_error(message)
