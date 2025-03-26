from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import ContextManager
from typing import cast

from cleo.commands.base_command import BaseCommand
from cleo.formatters.style import Style
from cleo.io.inputs.string_input import StringInput
from cleo.io.null_io import NullIO
from cleo.io.outputs.output import Verbosity
from cleo.ui.table_separator import TableSeparator


if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 8):
        from typing import Literal
    else:
        from typing_extensions import Literal

    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option
    from cleo.io.io import IO
    from cleo.ui.progress_bar import ProgressBar
    from cleo.ui.progress_indicator import ProgressIndicator
    from cleo.ui.question import Question
    from cleo.ui.table import Rows
    from cleo.ui.table import Table


class Command(BaseCommand):
    arguments: ClassVar[list[Argument]] = []
    options: ClassVar[list[Option]] = []
    aliases: ClassVar[list[str]] = []
    usages: ClassVar[list[str]] = []
    commands: ClassVar[list[BaseCommand]] = []

    def __init__(self) -> None:
        self._io: IO = None  # type: ignore[assignment]
        super().__init__()

    @property
    def io(self) -> IO:
        return self._io

    def configure(self) -> None:
        for argument in self.arguments:
            self._definition.add_argument(argument)

        for option in self.options:
            self._definition.add_option(option)

    def execute(self, io: IO) -> int:
        self._io = io

        try:
            return self.handle()
        except KeyboardInterrupt:
            return 1

    def handle(self) -> int:
        """
        Execute the command.
        """
        raise NotImplementedError

    def call(self, name: str, args: str | None = None) -> int:
        """
        Call another command.
        """
        assert self.application is not None
        command = self.application.get(name)

        return self.application._run_command(
            command, self._io.with_input(StringInput(args or ""))
        )

    def call_silent(self, name: str, args: str | None = None) -> int:
        """
        Call another command silently.
        """
        assert self.application is not None
        command = self.application.get(name)

        return self.application._run_command(command, NullIO(StringInput(args or "")))

    def argument(self, name: str) -> Any:
        """
        Get the value of a command argument.
        """
        return self._io.input.argument(name)

    def option(self, name: str) -> Any:
        """
        Get the value of a command option.
        """
        return self._io.input.option(name)

    def confirm(
        self, question: str, default: bool = False, true_answer_regex: str = r"(?i)^y"
    ) -> bool:
        """
        Confirm a question with the user.
        """
        from cleo.ui.confirmation_question import ConfirmationQuestion

        confirmation = ConfirmationQuestion(
            question, default=default, true_answer_regex=true_answer_regex
        )
        return cast(bool, confirmation.ask(self._io))

    def ask(self, question: str | Question, default: Any | None = None) -> Any:
        """
        Prompt the user for input.
        """
        from cleo.ui.question import Question

        if not isinstance(question, Question):
            question = Question(question, default=default)

        return question.ask(self._io)

    def secret(self, question: str | Question, default: Any | None = None) -> Any:
        """
        Prompt the user for input but hide the answer from the console.
        """
        from cleo.ui.question import Question

        if not isinstance(question, Question):
            question = Question(question, default=default)

        question.hide()

        return question.ask(self._io)

    def choice(
        self,
        question: str,
        choices: list[str],
        default: Any | None = None,
        attempts: int | None = None,
        multiple: bool = False,
    ) -> Any:
        """
        Give the user a single choice from an list of answers.
        """
        from cleo.ui.choice_question import ChoiceQuestion

        choice = ChoiceQuestion(question, choices, default)

        choice.set_max_attempts(attempts)
        choice.set_multi_select(multiple)

        return choice.ask(self._io)

    def create_question(
        self,
        question: str,
        type: Literal["choice", "confirmation"] | None = None,
        **kwargs: Any,
    ) -> Question:
        """
        Returns a Question of specified type.
        """
        from cleo.ui.choice_question import ChoiceQuestion
        from cleo.ui.confirmation_question import ConfirmationQuestion
        from cleo.ui.question import Question

        if type == "confirmation":
            return ConfirmationQuestion(question, **kwargs)

        if type == "choice":
            return ChoiceQuestion(question, **kwargs)

        return Question(question, **kwargs)

    def table(
        self,
        header: str | None = None,
        rows: Rows | None = None,
        style: str | None = None,
    ) -> Table:
        """
        Return a Table instance.
        """
        from cleo.ui.table import Table

        table = Table(self._io, style=style)

        if header:
            table.set_headers([header])

        if rows:
            table.set_rows(rows)

        return table

    def table_separator(self) -> TableSeparator:
        """
        Return a TableSeparator instance.
        """

        return TableSeparator()

    def render_table(self, headers: str, rows: Rows, style: str | None = None) -> None:
        """
        Format input to textual table.
        """
        table = self.table(headers, rows, style)

        table.render()

    def write(self, text: str, style: str | None = None) -> None:
        """
        Writes a string without a new line.
        Useful if you want to use overwrite().
        """
        styled = f"<{style}>{text}</>" if style else text

        self._io.write(styled)

    def line(
        self,
        text: str,
        style: str | None = None,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        """
        Write a string as information output.
        """
        styled = f"<{style}>{text}</>" if style else text

        self._io.write_line(styled, verbosity=verbosity)

    def line_error(
        self,
        text: str,
        style: str | None = None,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        """
        Write a string as information output to stderr.
        """
        styled = f"<{style}>{text}</>" if style else text

        self._io.write_error_line(styled, verbosity)

    def info(self, text: str) -> None:
        """
        Write a string as information output.

        :param text: The line to write
        :type text: str
        """
        self.line(text, "info")

    def comment(self, text: str) -> None:
        """
        Write a string as comment output.

        :param text: The line to write
        :type text: str
        """
        self.line(text, "comment")

    def question(self, text: str) -> None:
        """
        Write a string as question output.

        :param text: The line to write
        :type text: str
        """
        self.line(text, "question")

    def progress_bar(self, max: int = 0) -> ProgressBar:
        """
        Creates a new progress bar
        """
        from cleo.ui.progress_bar import ProgressBar

        return ProgressBar(self._io, max=max)

    def progress_indicator(
        self,
        fmt: str | None = None,
        interval: int = 100,
        values: list[str] | None = None,
    ) -> ProgressIndicator:
        """
        Creates a new progress indicator.
        """
        from cleo.ui.progress_indicator import ProgressIndicator

        return ProgressIndicator(self.io, fmt, interval, values)

    def spin(
        self,
        start_message: str,
        end_message: str,
        fmt: str | None = None,
        interval: int = 100,
        values: list[str] | None = None,
    ) -> ContextManager[ProgressIndicator]:
        """
        Automatically spin a progress indicator.
        """
        spinner = self.progress_indicator(fmt, interval, values)

        return spinner.auto(start_message, end_message)

    def add_style(
        self,
        name: str,
        fg: str | None = None,
        bg: str | None = None,
        options: list[str] | None = None,
    ) -> None:
        """
        Adds a new style
        """
        style = Style(fg, bg, options)
        self._io.output.formatter.set_style(name, style)
        self._io.error_output.formatter.set_style(name, style)

    def overwrite(self, text: str) -> None:
        """
        Overwrites the current line.

        It will not add a new line so use line('')
        if necessary.
        """
        self._io.overwrite(text)
