"""
Adapters for the enum type.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Mapping, Sequence, cast

from .. import errors as e
from .. import postgres, sql
from ..pq import Format
from ..abc import AdaptContext, Query
from ..adapt import Buffer, Dumper, Loader
from .._compat import TypeAlias, TypeVar, cache
from .._typeinfo import TypeInfo
from .._encodings import conn_encoding

if TYPE_CHECKING:
    from .._connection_base import BaseConnection

E = TypeVar("E", bound=Enum)

EnumDumpMap: TypeAlias = "dict[E, bytes]"
EnumLoadMap: TypeAlias = "dict[bytes, E]"
EnumMapping: TypeAlias = "Mapping[E, str] | Sequence[tuple[E, str]] | None"

# Hashable versions
_HEnumDumpMap: TypeAlias = "tuple[tuple[E, bytes], ...]"
_HEnumLoadMap: TypeAlias = "tuple[tuple[bytes, E], ...]"

TEXT = Format.TEXT
BINARY = Format.BINARY


class EnumInfo(TypeInfo):
    """Manage information about an enum type."""

    def __init__(
        self,
        name: str,
        oid: int,
        array_oid: int,
        labels: Sequence[str],
    ):
        super().__init__(name, oid, array_oid)
        self.labels = labels
        # Will be set by register_enum()
        self.enum: type[Enum] | None = None

    @classmethod
    def _get_info_query(cls, conn: BaseConnection[Any]) -> Query:
        return sql.SQL(
            """\
SELECT name, oid, array_oid, array_agg(label) AS labels
FROM (
    SELECT
        t.typname AS name, t.oid AS oid, t.typarray AS array_oid,
        e.enumlabel AS label
    FROM pg_type t
    LEFT JOIN  pg_enum e
    ON e.enumtypid = t.oid
    WHERE t.oid = {regtype}
    ORDER BY e.enumsortorder
) x
GROUP BY name, oid, array_oid
"""
        ).format(regtype=cls._to_regtype(conn))


class _BaseEnumLoader(Loader, Generic[E]):
    """
    Loader for a specific Enum class
    """

    enum: type[E]
    _load_map: EnumLoadMap[E]

    def load(self, data: Buffer) -> E:
        if not isinstance(data, bytes):
            data = bytes(data)

        try:
            return self._load_map[data]
        except KeyError:
            enc = conn_encoding(self.connection)
            label = data.decode(enc, "replace")
            raise e.DataError(
                f"bad member for enum {self.enum.__qualname__}: {label!r}"
            )


class _BaseEnumDumper(Dumper, Generic[E]):
    """
    Dumper for a specific Enum class
    """

    enum: type[E]
    _dump_map: EnumDumpMap[E]

    def dump(self, value: E) -> Buffer | None:
        return self._dump_map[value]


class EnumDumper(Dumper):
    """
    Dumper for a generic Enum class
    """

    def __init__(self, cls: type, context: AdaptContext | None = None):
        super().__init__(cls, context)
        self._encoding = conn_encoding(self.connection)

    def dump(self, value: E) -> Buffer | None:
        return value.name.encode(self._encoding)


class EnumBinaryDumper(EnumDumper):
    format = BINARY


def register_enum(
    info: EnumInfo,
    context: AdaptContext | None = None,
    enum: type[E] | None = None,
    *,
    mapping: EnumMapping[E] = None,
) -> None:
    """Register the adapters to load and dump a enum type.

    :param info: The object with the information about the enum to register.
    :param context: The context where to register the adapters. If `!None`,
        register it globally.
    :param enum: Python enum type matching to the PostgreSQL one. If `!None`,
        a new enum will be generated and exposed as `EnumInfo.enum`.
    :param mapping: Override the mapping between `!enum` members and `!info`
        labels.
    """

    if not info:
        raise TypeError("no info passed. Is the requested enum available?")

    if enum is None:
        enum = cast("type[E]", _make_enum(info.name, tuple(info.labels)))

    info.enum = enum
    adapters = context.adapters if context else postgres.adapters
    info.register(context)

    load_map = _make_load_map(info, enum, mapping, context)

    loader = _make_loader(info.name, info.enum, load_map)
    adapters.register_loader(info.oid, loader)

    loader = _make_binary_loader(info.name, info.enum, load_map)
    adapters.register_loader(info.oid, loader)

    dump_map = _make_dump_map(info, enum, mapping, context)

    dumper = _make_dumper(info.enum, info.oid, dump_map)
    adapters.register_dumper(info.enum, dumper)

    dumper = _make_binary_dumper(info.enum, info.oid, dump_map)
    adapters.register_dumper(info.enum, dumper)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_enum(name: str, labels: tuple[str, ...]) -> Enum:
    return Enum(name.title(), labels, module=__name__)


@cache
def _make_loader(
    name: str, enum: type[Enum], load_map: _HEnumLoadMap[E]
) -> type[_BaseEnumLoader[E]]:
    attribs = {"enum": enum, "_load_map": dict(load_map)}
    return type(f"{name.title()}Loader", (_BaseEnumLoader,), attribs)


@cache
def _make_binary_loader(
    name: str, enum: type[Enum], load_map: _HEnumLoadMap[E]
) -> type[_BaseEnumLoader[E]]:
    attribs = {"enum": enum, "_load_map": dict(load_map), "format": BINARY}
    return type(f"{name.title()}BinaryLoader", (_BaseEnumLoader,), attribs)


@cache
def _make_dumper(
    enum: type[Enum], oid: int, dump_map: _HEnumDumpMap[E]
) -> type[_BaseEnumDumper[E]]:
    attribs = {"enum": enum, "oid": oid, "_dump_map": dict(dump_map)}
    return type(f"{enum.__name__}Dumper", (_BaseEnumDumper,), attribs)


@cache
def _make_binary_dumper(
    enum: type[Enum], oid: int, dump_map: _HEnumDumpMap[E]
) -> type[_BaseEnumDumper[E]]:
    attribs = {"enum": enum, "oid": oid, "_dump_map": dict(dump_map), "format": BINARY}
    return type(f"{enum.__name__}BinaryDumper", (_BaseEnumDumper,), attribs)


def _make_load_map(
    info: EnumInfo, enum: type[E], mapping: EnumMapping[E], context: AdaptContext | None
) -> _HEnumLoadMap[E]:
    enc = conn_encoding(context.connection if context else None)
    rv = []
    for label in info.labels:
        try:
            member = enum[label]
        except KeyError:
            # tolerate a missing enum, assuming it won't be used. If it is we
            # will get a DataError on fetch.
            pass
        else:
            rv.append((label.encode(enc), member))

    if mapping:
        if isinstance(mapping, Mapping):
            mapping = list(mapping.items())

        for member, label in mapping:
            rv.append((label.encode(enc), member))

    return tuple(rv)


def _make_dump_map(
    info: EnumInfo, enum: type[E], mapping: EnumMapping[E], context: AdaptContext | None
) -> _HEnumDumpMap[E]:
    enc = conn_encoding(context.connection if context else None)
    rv = []
    for member in enum:
        rv.append((member, member.name.encode(enc)))

    if mapping:
        if isinstance(mapping, Mapping):
            mapping = list(mapping.items())

        for member, label in mapping:
            rv.append((member, label.encode(enc)))

    return tuple(rv)


def register_default_adapters(context: AdaptContext) -> None:
    context.adapters.register_dumper(Enum, EnumBinaryDumper)
    context.adapters.register_dumper(Enum, EnumDumper)
