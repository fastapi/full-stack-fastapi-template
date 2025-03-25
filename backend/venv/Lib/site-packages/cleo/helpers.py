from __future__ import annotations

from typing import Any

from cleo.io.inputs.argument import Argument
from cleo.io.inputs.option import Option


def argument(
    name: str,
    description: str | None = None,
    optional: bool = False,
    multiple: bool = False,
    default: Any | None = None,
) -> Argument:
    return Argument(
        name,
        required=not optional,
        is_list=multiple,
        description=description,
        default=default,
    )


def option(
    long_name: str,
    short_name: str | None = None,
    description: str | None = None,
    flag: bool = True,
    value_required: bool = True,
    multiple: bool = False,
    default: Any | None = None,
) -> Option:
    return Option(
        long_name,
        short_name,
        flag=flag,
        requires_value=value_required,
        is_list=multiple,
        description=description,
        default=default,
    )
