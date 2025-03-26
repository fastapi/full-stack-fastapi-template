"""
psycopg row factories
"""

# Copyright (C) 2021 The Psycopg Team

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable, Dict  # drop with Python 3.8
from typing import NamedTuple, NoReturn, Protocol, Sequence, Tuple
from collections import namedtuple

from . import errors as e
from . import pq
from ._compat import TypeAlias, TypeVar
from ._encodings import _as_python_identifier

if TYPE_CHECKING:
    from psycopg.pq.abc import PGresult

    from .cursor import Cursor
    from ._cursor_base import BaseCursor
    from .cursor_async import AsyncCursor

COMMAND_OK = pq.ExecStatus.COMMAND_OK
TUPLES_OK = pq.ExecStatus.TUPLES_OK
SINGLE_TUPLE = pq.ExecStatus.SINGLE_TUPLE
TUPLES_CHUNK = pq.ExecStatus.TUPLES_CHUNK

T = TypeVar("T", covariant=True)

# Row factories

Row = TypeVar("Row", covariant=True, default="TupleRow")


class RowMaker(Protocol[Row]):
    """
    Callable protocol taking a sequence of value and returning an object.

    The sequence of value is what is returned from a database query, already
    adapted to the right Python types. The return value is the object that your
    program would like to receive: by default (`tuple_row()`) it is a simple
    tuple, but it may be any type of object.

    Typically, `!RowMaker` functions are returned by `RowFactory`.
    """

    def __call__(self, __values: Sequence[Any]) -> Row: ...


class RowFactory(Protocol[Row]):
    """
    Callable protocol taking a `~psycopg.Cursor` and returning a `RowMaker`.

    A `!RowFactory` is typically called when a `!Cursor` receives a result.
    This way it can inspect the cursor state (for instance the
    `~psycopg.Cursor.description` attribute) and help a `!RowMaker` to create
    a complete object.

    For instance the `dict_row()` `!RowFactory` uses the names of the column to
    define the dictionary key and returns a `!RowMaker` function which would
    use the values to create a dictionary for each record.
    """

    def __call__(self, __cursor: Cursor[Any]) -> RowMaker[Row]: ...


class AsyncRowFactory(Protocol[Row]):
    """
    Like `RowFactory`, taking an async cursor as argument.
    """

    def __call__(self, __cursor: AsyncCursor[Any]) -> RowMaker[Row]: ...


class BaseRowFactory(Protocol[Row]):
    """
    Like `RowFactory`, taking either type of cursor as argument.
    """

    def __call__(self, __cursor: BaseCursor[Any, Any]) -> RowMaker[Row]: ...


TupleRow: TypeAlias = Tuple[Any, ...]
"""
An alias for the type returned by `tuple_row()` (i.e. a tuple of any content).
"""


DictRow: TypeAlias = Dict[str, Any]
"""
An alias for the type returned by `dict_row()`

A `!DictRow` is a dictionary with keys as string and any value returned by the
database.
"""


def tuple_row(cursor: BaseCursor[Any, Any]) -> RowMaker[TupleRow]:
    r"""Row factory to represent rows as simple tuples.

    This is the default factory, used when `~psycopg.Connection.connect()` or
    `~psycopg.Connection.cursor()` are called without a `!row_factory`
    parameter.

    """
    # Implementation detail: make sure this is the tuple type itself, not an
    # equivalent function, because the C code fast-paths on it.
    return tuple


def dict_row(cursor: BaseCursor[Any, Any]) -> RowMaker[DictRow]:
    """Row factory to represent rows as dictionaries.

    The dictionary keys are taken from the column names of the returned columns.
    """
    names = _get_names(cursor)
    if names is None:
        return no_result

    def dict_row_(values: Sequence[Any]) -> dict[str, Any]:
        return dict(zip(names, values))

    return dict_row_


def namedtuple_row(cursor: BaseCursor[Any, Any]) -> RowMaker[NamedTuple]:
    """Row factory to represent rows as `~collections.namedtuple`.

    The field names are taken from the column names of the returned columns,
    with some mangling to deal with invalid names.
    """
    res = cursor.pgresult
    if not res:
        return no_result

    nfields = _get_nfields(res)
    if nfields is None:
        return no_result

    nt = _make_nt(cursor._encoding, *(res.fname(i) for i in range(nfields)))
    return nt._make


@functools.lru_cache(512)
def _make_nt(enc: str, *names: bytes) -> type[NamedTuple]:
    snames = tuple(_as_python_identifier(n.decode(enc)) for n in names)
    return namedtuple("Row", snames)  # type: ignore[return-value]


def class_row(cls: type[T]) -> BaseRowFactory[T]:
    r"""Generate a row factory to represent rows as instances of the class `!cls`.

    The class must support every output column name as a keyword parameter.

    :param cls: The class to return for each row. It must support the fields
        returned by the query as keyword arguments.
    :rtype: `!Callable[[Cursor],` `RowMaker`\[~T]]
    """

    def class_row_(cursor: BaseCursor[Any, Any]) -> RowMaker[T]:
        names = _get_names(cursor)
        if names is None:
            return no_result

        def class_row__(values: Sequence[Any]) -> T:
            return cls(**dict(zip(names, values)))

        return class_row__

    return class_row_


def args_row(func: Callable[..., T]) -> BaseRowFactory[T]:
    """Generate a row factory calling `!func` with positional parameters for every row.

    :param func: The function to call for each row. It must support the fields
        returned by the query as positional arguments.
    """

    def args_row_(cur: BaseCursor[Any, T]) -> RowMaker[T]:
        def args_row__(values: Sequence[Any]) -> T:
            return func(*values)

        return args_row__

    return args_row_


def kwargs_row(func: Callable[..., T]) -> BaseRowFactory[T]:
    """Generate a row factory calling `!func` with keyword parameters for every row.

    :param func: The function to call for each row. It must support the fields
        returned by the query as keyword arguments.
    """

    def kwargs_row_(cursor: BaseCursor[Any, T]) -> RowMaker[T]:
        names = _get_names(cursor)
        if names is None:
            return no_result

        def kwargs_row__(values: Sequence[Any]) -> T:
            return func(**dict(zip(names, values)))

        return kwargs_row__

    return kwargs_row_


def scalar_row(cursor: BaseCursor[Any, Any]) -> RowMaker[Any]:
    """
    Generate a row factory returning the first column
    as a scalar value.
    """
    res = cursor.pgresult
    if not res:
        return no_result

    nfields = _get_nfields(res)
    if nfields is None:
        return no_result

    if nfields < 1:
        raise e.ProgrammingError("at least one column expected")

    def scalar_row_(values: Sequence[Any]) -> Any:
        return values[0]

    return scalar_row_


def no_result(values: Sequence[Any]) -> NoReturn:
    """A `RowMaker` that always fail.

    It can be used as return value for a `RowFactory` called with no result.
    Note that the `!RowFactory` *will* be called with no result, but the
    resulting `!RowMaker` never should.
    """
    raise e.InterfaceError("the cursor doesn't have a result")


def _get_names(cursor: BaseCursor[Any, Any]) -> list[str] | None:
    res = cursor.pgresult
    if not res:
        return None

    nfields = _get_nfields(res)
    if nfields is None:
        return None

    enc = cursor._encoding
    return [
        res.fname(i).decode(enc) for i in range(nfields)  # type: ignore[union-attr]
    ]


def _get_nfields(res: PGresult) -> int | None:
    """
    Return the number of columns in a result, if it returns tuples else None

    Take into account the special case of results with zero columns.
    """
    nfields = res.nfields

    if (
        res.status == TUPLES_OK
        or res.status == SINGLE_TUPLE
        or res.status == TUPLES_CHUNK
        # "describe" in named cursors
        or (res.status == COMMAND_OK and nfields)
    ):
        return nfields
    else:
        return None
