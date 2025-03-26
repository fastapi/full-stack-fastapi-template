from __future__ import annotations

from cleo._utils import find_similar_names


class CleoError(Exception):
    """
    Base Cleo exception.
    """

    exit_code: int | None = None


class CleoLogicError(CleoError):
    """
    Raised when there is error in command arguments
    and/or options configuration logic.
    """


class CleoRuntimeError(CleoError):
    """
    Raised when command is called with invalid options or arguments.
    """


class CleoValueError(CleoError):
    """
    Raised when wrong value was given to Cleo components.
    """


class CleoNoSuchOptionError(CleoError):
    """
    Raised when command does not have given option.
    """


class CleoUserError(CleoError):
    """
    Base exception for user errors.
    """


class CleoMissingArgumentsError(CleoUserError):
    """
    Raised when called command was not given required arguments.
    """


def _suggest_similar_names(name: str, names: list[str]) -> str | None:
    if not names:
        return None

    suggested_names = find_similar_names(name, names)

    if not suggested_names:
        return None

    newline_separator = "\n    "
    return "Did you mean " + newline_separator.join(
        (
            ("this?" if len(suggested_names) == 1 else "one of these?"),
            newline_separator.join(suggested_names),
        )
    )


class CleoCommandNotFoundError(CleoUserError):
    """
    Raised when called command does not exist.
    """

    def __init__(self, name: str, commands: list[str] | None = None) -> None:
        message = f'The command "{name}" does not exist.'
        if commands:
            suggestions = _suggest_similar_names(name, commands)
            if suggestions:
                message += "\n\n" + suggestions
        super().__init__(message)


class CleoNamespaceNotFoundError(CleoUserError):
    """
    Raised when called namespace has no commands.
    """

    def __init__(self, name: str, namespaces: list[str] | None = None) -> None:
        message = f'There are no commands in the "{name}" namespace.'
        if namespaces:
            suggestions = _suggest_similar_names(name, namespaces)
            if suggestions:
                message += "\n\n" + suggestions
        super().__init__(message)
