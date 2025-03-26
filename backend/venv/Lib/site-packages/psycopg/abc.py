"""
Protocol objects representing different implementations of the same classes.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict  # drop with Python 3.8
from typing import Generator, Mapping, Protocol, Sequence, Union

from . import pq
from ._enums import PyFormat as PyFormat
from ._compat import LiteralString, TypeAlias, TypeVar

if TYPE_CHECKING:
    from . import sql  # noqa: F401
    from .rows import Row, RowMaker
    from .pq.abc import PGresult
    from .waiting import Ready, Wait  # noqa: F401
    from ._adapters_map import AdaptersMap
    from ._connection_base import BaseConnection

NoneType: type = type(None)

# An object implementing the buffer protocol
Buffer: TypeAlias = Union[bytes, bytearray, memoryview]

Query: TypeAlias = Union[LiteralString, bytes, "sql.SQL", "sql.Composed"]
Params: TypeAlias = Union[Sequence[Any], Mapping[str, Any]]
ConnectionType = TypeVar("ConnectionType", bound="BaseConnection[Any]")
PipelineCommand: TypeAlias = Callable[[], None]
DumperKey: TypeAlias = Union[type, "tuple[DumperKey, ...]"]
ConnParam: TypeAlias = Union[str, int, None]
ConnDict: TypeAlias = Dict[str, ConnParam]
ConnMapping: TypeAlias = Mapping[str, ConnParam]


# Waiting protocol types

RV = TypeVar("RV")

PQGenConn: TypeAlias = Generator["tuple[int, Wait]", "Ready | int", RV]
"""Generator for processes where the connection file number can change.

This can happen in connection and reset, but not in normal querying.
"""

PQGen: TypeAlias = Generator["Wait", "Ready | int", RV]
"""Generator for processes where the connection file number won't change.
"""


class WaitFunc(Protocol):
    """
    Wait on the connection which generated `PQgen` and return its final result.
    """

    def __call__(
        self, gen: PQGen[RV], fileno: int, interval: float | None = None
    ) -> RV: ...


# Adaptation types

DumpFunc: TypeAlias = Callable[[Any], "Buffer | None"]
LoadFunc: TypeAlias = Callable[[Buffer], Any]


class AdaptContext(Protocol):
    """
    A context describing how types are adapted.

    Example of `~AdaptContext` are `~psycopg.Connection`, `~psycopg.Cursor`,
    `~psycopg.adapt.Transformer`, `~psycopg.adapt.AdaptersMap`.

    Note that this is a `~typing.Protocol`, so objects implementing
    `!AdaptContext` don't need to explicitly inherit from this class.

    """

    @property
    def adapters(self) -> AdaptersMap:
        """The adapters configuration that this object uses."""
        ...

    @property
    def connection(self) -> BaseConnection[Any] | None:
        """The connection used by this object, if available.

        :rtype: `~psycopg.Connection` or `~psycopg.AsyncConnection` or `!None`
        """
        ...


class Dumper(Protocol):
    """
    Convert Python objects of type `!cls` to PostgreSQL representation.
    """

    format: pq.Format
    """
    The format that this class `dump()` method produces,
    `~psycopg.pq.Format.TEXT` or `~psycopg.pq.Format.BINARY`.

    This is a class attribute.
    """

    oid: int
    """The oid to pass to the server, if known; 0 otherwise (class attribute)."""

    def __init__(self, cls: type, context: AdaptContext | None = None): ...

    def dump(self, obj: Any) -> Buffer | None:
        """Convert the object `!obj` to PostgreSQL representation.

        :param obj: the object to convert.
        """
        ...

    def quote(self, obj: Any) -> Buffer:
        """Convert the object `!obj` to escaped representation.

        :param obj: the object to convert.
        """
        ...

    def get_key(self, obj: Any, format: PyFormat) -> DumperKey:
        """Return an alternative key to upgrade the dumper to represent `!obj`.

        :param obj: The object to convert
        :param format: The format to convert to

        Normally the type of the object is all it takes to define how to dump
        the object to the database. For instance, a Python `~datetime.date` can
        be simply converted into a PostgreSQL :sql:`date`.

        In a few cases, just the type is not enough. For example:

        - A Python `~datetime.datetime` could be represented as a
          :sql:`timestamptz` or a :sql:`timestamp`, according to whether it
          specifies a `!tzinfo` or not.

        - A Python int could be stored as several Postgres types: int2, int4,
          int8, numeric. If a type too small is used, it may result in an
          overflow. If a type too large is used, PostgreSQL may not want to
          cast it to a smaller type.

        - Python lists should be dumped according to the type they contain to
          convert them to e.g. array of strings, array of ints (and which
          size of int?...)

        In these cases, a dumper can implement `!get_key()` and return a new
        class, or sequence of classes, that can be used to identify the same
        dumper again. If the mechanism is not needed, the method should return
        the same `!cls` object passed in the constructor.

        If a dumper implements `get_key()` it should also implement
        `upgrade()`.

        """
        ...

    def upgrade(self, obj: Any, format: PyFormat) -> Dumper:
        """Return a new dumper to manage `!obj`.

        :param obj: The object to convert
        :param format: The format to convert to

        Once `Transformer.get_dumper()` has been notified by `get_key()` that
        this Dumper class cannot handle `!obj` itself, it will invoke
        `!upgrade()`, which should return a new `Dumper` instance, which will
        be reused for every objects for which `!get_key()` returns the same
        result.
        """
        ...


class Loader(Protocol):
    """
    Convert PostgreSQL values with type OID `!oid` to Python objects.
    """

    format: pq.Format
    """
    The format that this class `load()` method can convert,
    `~psycopg.pq.Format.TEXT` or `~psycopg.pq.Format.BINARY`.

    This is a class attribute.
    """

    def __init__(self, oid: int, context: AdaptContext | None = None): ...

    def load(self, data: Buffer) -> Any:
        """
        Convert the data returned by the database into a Python object.

        :param data: the data to convert.
        """
        ...


class Transformer(Protocol):
    types: tuple[int, ...] | None
    formats: list[pq.Format] | None

    def __init__(self, context: AdaptContext | None = None): ...

    @classmethod
    def from_context(cls, context: AdaptContext | None) -> Transformer: ...

    @property
    def connection(self) -> BaseConnection[Any] | None: ...

    @property
    def encoding(self) -> str: ...

    @property
    def adapters(self) -> AdaptersMap: ...

    @property
    def pgresult(self) -> PGresult | None: ...

    def set_pgresult(
        self,
        result: PGresult | None,
        *,
        set_loaders: bool = True,
        format: pq.Format | None = None,
    ) -> None: ...

    def set_dumper_types(self, types: Sequence[int], format: pq.Format) -> None: ...

    def set_loader_types(self, types: Sequence[int], format: pq.Format) -> None: ...

    def dump_sequence(
        self, params: Sequence[Any], formats: Sequence[PyFormat]
    ) -> Sequence[Buffer | None]: ...

    def as_literal(self, obj: Any) -> bytes: ...

    def get_dumper(self, obj: Any, format: PyFormat) -> Dumper: ...

    def load_rows(self, row0: int, row1: int, make_row: RowMaker[Row]) -> list[Row]: ...

    def load_row(self, row: int, make_row: RowMaker[Row]) -> Row | None: ...

    def load_sequence(self, record: Sequence[Buffer | None]) -> tuple[Any, ...]: ...

    def get_loader(self, oid: int, format: pq.Format) -> Loader: ...
