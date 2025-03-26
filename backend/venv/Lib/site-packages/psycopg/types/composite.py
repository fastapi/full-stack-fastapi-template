"""
Support for composite types adaptation.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import re
import struct
from typing import TYPE_CHECKING, Any, Callable, Iterator, NamedTuple, Sequence, cast
from collections import namedtuple

from .. import abc, postgres, pq, sql
from .._oids import TEXT_OID
from ..adapt import Buffer, Dumper, Loader, PyFormat, RecursiveDumper, Transformer
from .._compat import cache
from .._struct import pack_len, unpack_len
from .._typeinfo import TypeInfo
from .._encodings import _as_python_identifier

if TYPE_CHECKING:
    from .._connection_base import BaseConnection

_struct_oidlen = struct.Struct("!Ii")
_pack_oidlen = cast(Callable[[int, int], bytes], _struct_oidlen.pack)
_unpack_oidlen = cast(
    Callable[[abc.Buffer, int], "tuple[int, int]"], _struct_oidlen.unpack_from
)


class CompositeInfo(TypeInfo):
    """Manage information about a composite type."""

    def __init__(
        self,
        name: str,
        oid: int,
        array_oid: int,
        *,
        regtype: str = "",
        field_names: Sequence[str],
        field_types: Sequence[int],
    ):
        super().__init__(name, oid, array_oid, regtype=regtype)
        self.field_names = field_names
        self.field_types = field_types
        # Will be set by register() if the `factory` is a type
        self.python_type: type | None = None

    @classmethod
    def _get_info_query(cls, conn: BaseConnection[Any]) -> abc.Query:
        return sql.SQL(
            """\
SELECT
    t.typname AS name, t.oid AS oid, t.typarray AS array_oid,
    t.oid::regtype::text AS regtype,
    coalesce(a.fnames, '{{}}') AS field_names,
    coalesce(a.ftypes, '{{}}') AS field_types
FROM pg_type t
LEFT JOIN (
    SELECT
        attrelid,
        array_agg(attname) AS fnames,
        array_agg(atttypid) AS ftypes
    FROM (
        SELECT a.attrelid, a.attname, a.atttypid
        FROM pg_attribute a
        JOIN pg_type t ON t.typrelid = a.attrelid
        WHERE t.oid = {regtype}
        AND a.attnum > 0
        AND NOT a.attisdropped
        ORDER BY a.attnum
    ) x
    GROUP BY attrelid
) a ON a.attrelid = t.typrelid
WHERE t.oid = {regtype}
"""
        ).format(regtype=cls._to_regtype(conn))


class SequenceDumper(RecursiveDumper):
    def _dump_sequence(
        self, obj: Sequence[Any], start: bytes, end: bytes, sep: bytes
    ) -> bytes:
        if not obj:
            return start + end

        parts: list[abc.Buffer] = [start]

        for item in obj:
            if item is None:
                parts.append(sep)
                continue

            dumper = self._tx.get_dumper(item, PyFormat.from_pq(self.format))
            ad = dumper.dump(item)
            if ad is None:
                ad = b""
            elif not ad:
                ad = b'""'
            elif self._re_needs_quotes.search(ad):
                ad = b'"' + self._re_esc.sub(rb"\1\1", ad) + b'"'

            parts.append(ad)
            parts.append(sep)

        parts[-1] = end

        return b"".join(parts)

    _re_needs_quotes = re.compile(rb'[",\\\s()]')
    _re_esc = re.compile(rb"([\\\"])")


class TupleDumper(SequenceDumper):
    # Should be this, but it doesn't work
    # oid = _oids.RECORD_OID

    def dump(self, obj: tuple[Any, ...]) -> Buffer | None:
        return self._dump_sequence(obj, b"(", b")", b",")


class TupleBinaryDumper(Dumper):
    format = pq.Format.BINARY

    # Subclasses must set this info
    _field_types: tuple[int, ...]

    def __init__(self, cls: type, context: abc.AdaptContext | None = None):
        super().__init__(cls, context)

        # Note: this class is not a RecursiveDumper because it would use the
        # same Transformer of the context, which would confuse dump_sequence()
        # in case the composite contains another composite. Make sure to use
        # a separate Transformer instance instead.
        self._tx = Transformer(context)
        self._tx.set_dumper_types(self._field_types, self.format)

        nfields = len(self._field_types)
        self._formats = (PyFormat.from_pq(self.format),) * nfields

    def dump(self, obj: tuple[Any, ...]) -> Buffer | None:
        out = bytearray(pack_len(len(obj)))
        adapted = self._tx.dump_sequence(obj, self._formats)
        for i in range(len(obj)):
            b = adapted[i]
            oid = self._field_types[i]
            if b is not None:
                out += _pack_oidlen(oid, len(b))
                out += b
            else:
                out += _pack_oidlen(oid, -1)

        return out


class BaseCompositeLoader(Loader):
    def __init__(self, oid: int, context: abc.AdaptContext | None = None):
        super().__init__(oid, context)
        self._tx = Transformer(context)

    def _parse_record(self, data: abc.Buffer) -> Iterator[bytes | None]:
        """
        Split a non-empty representation of a composite type into components.

        Terminators shouldn't be used in `!data` (so that both record and range
        representations can be parsed).
        """
        for m in self._re_tokenize.finditer(data):
            if m.group(1):
                yield None
            elif m.group(2) is not None:
                yield self._re_undouble.sub(rb"\1", m.group(2))
            else:
                yield m.group(3)

        # If the final group ended in `,` there is a final NULL in the record
        # that the regexp couldn't parse.
        if m and m.group().endswith(b","):
            yield None

    _re_tokenize = re.compile(
        rb"""(?x)
          (,)                       # an empty token, representing NULL
        | " ((?: [^"] | "")*) " ,?  # or a quoted string
        | ([^",)]+) ,?              # or an unquoted string
        """
    )

    _re_undouble = re.compile(rb'(["\\])\1')


class RecordLoader(BaseCompositeLoader):
    def load(self, data: abc.Buffer) -> tuple[Any, ...]:
        if data == b"()":
            return ()

        cast = self._tx.get_loader(TEXT_OID, self.format).load
        return tuple(
            cast(token) if token is not None else None
            for token in self._parse_record(data[1:-1])
        )


class RecordBinaryLoader(Loader):
    format = pq.Format.BINARY

    def __init__(self, oid: int, context: abc.AdaptContext | None = None):
        super().__init__(oid, context)
        self._ctx = context
        # Cache a transformer for each sequence of oid found.
        # Usually there will be only one, but if there is more than one
        # row in the same query (in different columns, or even in different
        # records), oids might differ and we'd need separate transformers.
        self._txs: dict[tuple[int, ...], abc.Transformer] = {}

    def load(self, data: abc.Buffer) -> tuple[Any, ...]:
        nfields = unpack_len(data, 0)[0]
        offset = 4
        oids = []
        record = []
        for _ in range(nfields):
            oid, length = _unpack_oidlen(data, offset)
            offset += 8
            record.append(data[offset : offset + length] if length != -1 else None)
            oids.append(oid)
            if length >= 0:
                offset += length

        key = tuple(oids)
        try:
            tx = self._txs[key]
        except KeyError:
            tx = self._txs[key] = Transformer(self._ctx)
            tx.set_loader_types(oids, self.format)

        return tx.load_sequence(tuple(record))


class CompositeLoader(RecordLoader):
    factory: Callable[..., Any]
    fields_types: list[int]
    _types_set = False

    def load(self, data: abc.Buffer) -> Any:
        if not self._types_set:
            self._config_types(data)
            self._types_set = True

        if data == b"()":
            return type(self).factory()

        return type(self).factory(
            *self._tx.load_sequence(tuple(self._parse_record(data[1:-1])))
        )

    def _config_types(self, data: abc.Buffer) -> None:
        self._tx.set_loader_types(self.fields_types, self.format)


class CompositeBinaryLoader(RecordBinaryLoader):
    format = pq.Format.BINARY
    factory: Callable[..., Any]

    def load(self, data: abc.Buffer) -> Any:
        r = super().load(data)
        return type(self).factory(*r)


def register_composite(
    info: CompositeInfo,
    context: abc.AdaptContext | None = None,
    factory: Callable[..., Any] | None = None,
) -> None:
    """Register the adapters to load and dump a composite type.

    :param info: The object with the information about the composite to register.
    :param context: The context where to register the adapters. If `!None`,
        register it globally.
    :param factory: Callable to convert the sequence of attributes read from
        the composite into a Python object.

    .. note::

        Registering the adapters doesn't affect objects already created, even
        if they are children of the registered context. For instance,
        registering the adapter globally doesn't affect already existing
        connections.
    """

    # A friendly error warning instead of an AttributeError in case fetch()
    # failed and it wasn't noticed.
    if not info:
        raise TypeError("no info passed. Is the requested composite available?")

    # Register arrays and type info
    info.register(context)

    if not factory:
        factory = _nt_from_info(info)

    adapters = context.adapters if context else postgres.adapters

    # generate and register a customized text loader
    loader: type[BaseCompositeLoader]
    loader = _make_loader(info.name, tuple(info.field_types), factory)
    adapters.register_loader(info.oid, loader)

    # generate and register a customized binary loader
    loader = _make_binary_loader(info.name, factory)
    adapters.register_loader(info.oid, loader)

    # If the factory is a type, create and register dumpers for it
    if isinstance(factory, type):
        dumper: type[Dumper]
        dumper = _make_binary_dumper(info.name, info.oid, tuple(info.field_types))
        adapters.register_dumper(factory, dumper)

        # Default to the text dumper because it is more flexible
        dumper = _make_dumper(info.name, info.oid)
        adapters.register_dumper(factory, dumper)

        info.python_type = factory


def register_default_adapters(context: abc.AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper(tuple, TupleDumper)
    adapters.register_loader("record", RecordLoader)
    adapters.register_loader("record", RecordBinaryLoader)


def _nt_from_info(info: CompositeInfo) -> type[NamedTuple]:
    name = _as_python_identifier(info.name)
    fields = tuple(_as_python_identifier(n) for n in info.field_names)
    return _make_nt(name, fields)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_nt(name: str, fields: tuple[str, ...]) -> type[NamedTuple]:
    return namedtuple(name, fields)  # type: ignore[return-value]


@cache
def _make_loader(
    name: str, types: tuple[int, ...], factory: Callable[..., Any]
) -> type[BaseCompositeLoader]:
    return type(
        f"{name.title()}Loader",
        (CompositeLoader,),
        {"factory": factory, "fields_types": list(types)},
    )


@cache
def _make_binary_loader(
    name: str, factory: Callable[..., Any]
) -> type[BaseCompositeLoader]:
    return type(
        f"{name.title()}BinaryLoader", (CompositeBinaryLoader,), {"factory": factory}
    )


@cache
def _make_dumper(name: str, oid: int) -> type[TupleDumper]:
    return type(f"{name.title()}Dumper", (TupleDumper,), {"oid": oid})


@cache
def _make_binary_dumper(
    name: str, oid: int, field_types: tuple[int, ...]
) -> type[TupleBinaryDumper]:
    return type(
        f"{name.title()}BinaryDumper",
        (TupleBinaryDumper,),
        {"oid": oid, "_field_types": field_types},
    )
