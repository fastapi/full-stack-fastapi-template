from __future__ import annotations

import sys

from typing import TYPE_CHECKING
from typing import Any

from cleo.exceptions import CleoNoSuchOptionError
from cleo.exceptions import CleoRuntimeError
from cleo.io.inputs.input import Input


if TYPE_CHECKING:
    from cleo.io.inputs.definition import Definition


class ArgvInput(Input):
    """
    Represents an input coming from the command line.
    """

    def __init__(
        self, argv: list[str] | None = None, definition: Definition | None = None
    ) -> None:
        if argv is None:
            argv = sys.argv

        argv = argv[:]

        # Strip the application name
        try:
            self._script_name: str | None = argv.pop(0)
        except IndexError:
            self._script_name = None

        self._tokens = argv
        self._parsed: list[str] = []

        super().__init__(definition=definition)

    @property
    def first_argument(self) -> str | None:
        is_option = False

        for i, token in enumerate(self._tokens):
            if token.startswith("-"):
                if "=" in token or len(self._tokens) == (i + 1):
                    continue

                # If it's a long option, consider that
                # everything after "--" is the option name.
                # Otherwise, use the last character
                # (if it's a short option set, only the last one
                # can take a value with space separator).
                name = token[2:] if token.startswith("--") else token[-1]

                if not (name in self._options or self._definition.has_shortcut(name)):
                    # noop
                    continue

                if name not in self._options:
                    name = self._definition.shortcut_to_name(name)

                if name in self._options and self._tokens[i + 1] == self._options[name]:
                    is_option = True

                continue

            if is_option:
                is_option = False
                continue

            return token

        return None

    @property
    def script_name(self) -> str | None:
        return self._script_name

    def has_parameter_option(
        self, values: str | list[str], only_params: bool = False
    ) -> bool:
        """
        Returns true if the raw parameters (not parsed) contain a value.
        """
        if not isinstance(values, list):
            values = [values]

        for token in self._tokens:
            if only_params and token == "--":
                return False

            for value in values:
                # Options with values:
                # For long options, test for '--option=' at beginning
                # For short options, test for '-o' at beginning
                leading = value + "=" if value.startswith("--") else value

                if token == value or leading != "" and token.startswith(leading):
                    return True

        return False

    def parameter_option(
        self,
        values: str | list[str],
        default: Any = False,
        only_params: bool = False,
    ) -> Any:
        if not isinstance(values, list):
            values = [values]

        tokens = self._tokens[:]
        while tokens:
            token = tokens.pop(0)
            if only_params and token == "--":
                return default

            for value in values:
                if token == value:
                    try:
                        return tokens.pop(0)
                    except IndexError:
                        return None

                # Options with values:
                # For long options, test for '--option=' at beginning
                # For short options, test for '-o' at beginning
                leading = value + "=" if value.startswith("--") else value

                if token == value or leading != "" and token.startswith(leading):
                    return token[len(leading)]

        return False

    def _set_tokens(self, tokens: list[str]) -> None:
        self._tokens = tokens

    def _parse(self) -> None:
        parse_options = True
        self._parsed = self._tokens[:]

        try:
            token = self._parsed.pop(0)
        except IndexError:
            return

        while token is not None:
            if parse_options and token == "":
                self._parse_argument(token)
            elif parse_options and token == "--":
                parse_options = False
            elif parse_options and token.startswith("--"):
                self._parse_long_option(token)
            elif parse_options and token.startswith("-") and token != "-":
                self._parse_short_option(token)
            else:
                self._parse_argument(token)

            try:
                token = self._parsed.pop(0)
            except IndexError:
                return

    def _parse_short_option(self, token: str) -> None:
        name = token[1:]

        if len(name) > 1:
            shortcut = name[0]
            if (
                self._definition.has_shortcut(shortcut)
                and self._definition.option_for_shortcut(shortcut).accepts_value()
            ):
                # An option with a value and no space
                self._add_short_option(shortcut, name[1:])
            else:
                self._parse_short_option_set(name)
        else:
            self._add_short_option(name, None)

    def _parse_short_option_set(self, name: str) -> None:
        length = len(name)
        for i in range(length):
            shortcut = name[i]
            if not self._definition.has_shortcut(shortcut):
                raise CleoRuntimeError(f'The option "{name[i]}" does not exist')

            option = self._definition.option_for_shortcut(shortcut)
            if option.accepts_value():
                self._add_long_option(
                    option.name, name[i + 1 :] if i < length - 1 else None
                )

                break

            self._add_long_option(option.name, None)

    def _parse_long_option(self, token: str) -> None:
        name = token[2:]

        pos = name.find("=")
        if pos != -1:
            value = name[pos + 1 :]
            if not value:
                self._parsed.insert(0, value)

            self._add_long_option(name[:pos], value)
        else:
            self._add_long_option(name, None)

    def _parse_argument(self, token: str) -> None:
        next_argument = len(self._arguments)
        last_argument = next_argument - 1

        # If the input is expecting another argument, add it
        if self._definition.has_argument(next_argument):
            argument = self._definition.argument(next_argument)
            self._arguments[argument.name] = [token] if argument.is_list() else token
        # If the last argument is a list, append the token to it
        elif (
            self._definition.has_argument(last_argument)
            and self._definition.argument(last_argument).is_list()
        ):
            argument = self._definition.argument(last_argument)
            self._arguments[argument.name].append(token)
        # Unexpected argument
        else:
            all_arguments = self._definition.arguments.copy()
            command_name = None
            argument = all_arguments[0]
            if argument and argument.name == "command":
                command_name = self._arguments.get("command")
                del all_arguments[0]

            if all_arguments:
                all_names = " ".join(a.name.join('""') for a in all_arguments)
                if command_name:
                    message = (
                        f'Too many arguments to "{command_name}" command, '
                        f"expected arguments {all_names}"
                    )
                else:
                    message = f"Too many arguments, expected arguments {all_names}"
            elif command_name:
                message = (
                    f'No arguments expected for "{command_name}" command, '
                    f'got "{token}"'
                )
            else:
                message = f'No arguments expected, got "{token}"'

            raise CleoRuntimeError(message)

    def _add_short_option(self, shortcut: str, value: Any) -> None:
        if not self._definition.has_shortcut(shortcut):
            raise CleoNoSuchOptionError(f'The option "-{shortcut}" does not exist')

        self._add_long_option(
            self._definition.option_for_shortcut(shortcut).name, value
        )

    def _add_long_option(self, name: str, value: Any) -> None:
        if not self._definition.has_option(name):
            raise CleoNoSuchOptionError(f'The option "--{name}" does not exist')

        option = self._definition.option(name)

        if not (value is None or option.accepts_value()):
            raise CleoRuntimeError(f'The "--{name}" option does not accept a value')

        if value in ("", None) and option.accepts_value() and self._parsed:
            # If the option accepts a value, either required or optional,
            # we check if there is one
            next_token = self._parsed.pop(0)
            if not next_token.startswith("-") or next_token in ("", None):
                value = next_token
            else:
                self._parsed.insert(0, next_token)

        if value is None:
            if option.requires_value():
                raise CleoRuntimeError(f'The "--{name}" option requires a value')

            if not option.is_list() and option.is_flag():
                value = True

        if option.is_list():
            if name not in self._options:
                self._options[name] = []

            self._options[name].append(value)
        else:
            self._options[name] = value
