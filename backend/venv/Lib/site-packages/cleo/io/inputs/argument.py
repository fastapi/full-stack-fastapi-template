from __future__ import annotations

from typing import Any

from cleo.exceptions import CleoLogicError


class Argument:
    """
    A command line argument.
    """

    def __init__(
        self,
        name: str,
        required: bool = True,
        is_list: bool = False,
        description: str | None = None,
        default: Any | None = None,
    ) -> None:
        self._name = name
        self._required = required
        self._is_list = is_list
        self._description = description or ""
        self._default: str | list[str] | None = None

        self.set_default(default)

    @property
    def name(self) -> str:
        return self._name

    @property
    def default(self) -> str | list[str] | None:
        return self._default

    @property
    def description(self) -> str:
        return self._description

    def is_required(self) -> bool:
        return self._required

    def is_list(self) -> bool:
        return self._is_list

    def set_default(self, default: Any | None = None) -> None:
        if self._required and default is not None:
            raise CleoLogicError("Cannot set a default value for required arguments")

        if self._is_list:
            if default is None:
                default = []
            elif not isinstance(default, list):
                raise CleoLogicError(
                    "A default value for a list argument must be a list"
                )

        self._default = default

    def __repr__(self) -> str:
        return (
            f"Argument({self._name!r}, "
            f"required={self._required}, "
            f"is_list={self._is_list}, "
            f"description={self._description!r}, "
            f"default={self._default!r})"
        )
