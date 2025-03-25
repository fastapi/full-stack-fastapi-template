"""
Support for multirange types adaptation.
"""

# Copyright (C) 2021 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterable, MutableSequence, overload
from decimal import Decimal
from datetime import date, datetime

from .. import _oids
from .. import errors as e
from .. import postgres, sql
from ..pq import Format
from ..abc import AdaptContext, Buffer, Dumper, DumperKey, Query
from .range import Range, T, dump_range_binary, dump_range_text, fail_dump
from .range import load_range_binary, load_range_text
from .._oids import INVALID_OID, TEXT_OID
from ..adapt import PyFormat, RecursiveDumper, RecursiveLoader
from .._compat import cache
from .._struct import pack_len, unpack_len
from .._typeinfo import TypeInfo, TypesRegistry

if TYPE_CHECKING:
    from .._connection_base import BaseConnection


class MultirangeInfo(TypeInfo):
    """Manage information about a multirange type."""

    def __init__(
        self,
        name: str,
        oid: int,
        array_oid: int,
        *,
        regtype: str = "",
        range_oid: int,
        subtype_oid: int,
    ):
        super().__init__(name, oid, array_oid, regtype=regtype)
        self.range_oid = range_oid
        self.subtype_oid = subtype_oid

    @classmethod
    def _get_info_query(cls, conn: BaseConnection[Any]) -> Query:
        if conn.info.server_version < 140000:
            raise e.NotSupportedError(
                "multirange types are only available from PostgreSQL 14"
            )
        return sql.SQL(
            """\
SELECT t.typname AS name, t.oid AS oid, t.typarray AS array_oid,
    t.oid::regtype::text AS regtype,
    r.rngtypid AS range_oid, r.rngsubtype AS subtype_oid
FROM pg_type t
JOIN pg_range r ON t.oid = r.rngmultitypid
WHERE t.oid = {regtype}
"""
        ).format(regtype=cls._to_regtype(conn))

    def _added(self, registry: TypesRegistry) -> None:
        # Map multiranges ranges and subtypes to info
        registry._registry[MultirangeInfo, self.range_oid] = self
        registry._registry[MultirangeInfo, self.subtype_oid] = self


class Multirange(MutableSequence[Range[T]]):
    """Python representation for a PostgreSQL multirange type.

    :param items: Sequence of ranges to initialise the object.
    """

    def __init__(self, items: Iterable[Range[T]] = ()):
        self._ranges: list[Range[T]] = list(map(self._check_type, items))

    def _check_type(self, item: Any) -> Range[Any]:
        if not isinstance(item, Range):
            raise TypeError(
                f"Multirange is a sequence of Range, got {type(item).__name__}"
            )
        return item

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._ranges!r})"

    def __str__(self) -> str:
        return f"{{{', '.join(map(str, self._ranges))}}}"

    @overload
    def __getitem__(self, index: int) -> Range[T]: ...

    @overload
    def __getitem__(self, index: slice) -> Multirange[T]: ...

    def __getitem__(self, index: int | slice) -> Range[T] | Multirange[T]:
        if isinstance(index, int):
            return self._ranges[index]
        else:
            return Multirange(self._ranges[index])

    def __len__(self) -> int:
        return len(self._ranges)

    @overload
    def __setitem__(self, index: int, value: Range[T]) -> None: ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[Range[T]]) -> None: ...

    def __setitem__(
        self, index: int | slice, value: Range[T] | Iterable[Range[T]]
    ) -> None:
        if isinstance(index, int):
            self._check_type(value)
            self._ranges[index] = self._check_type(value)
        elif not isinstance(value, Iterable):
            raise TypeError("can only assign an iterable")
        else:
            value = map(self._check_type, value)
            self._ranges[index] = value

    def __delitem__(self, index: int | slice) -> None:
        del self._ranges[index]

    def insert(self, index: int, value: Range[T]) -> None:
        self._ranges.insert(index, self._check_type(value))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Multirange):
            return False
        return self._ranges == other._ranges

    # Order is arbitrary but consistent

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Multirange):
            return NotImplemented
        return self._ranges < other._ranges

    def __le__(self, other: Any) -> bool:
        return self == other or self < other  # type: ignore

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Multirange):
            return NotImplemented
        return self._ranges > other._ranges

    def __ge__(self, other: Any) -> bool:
        return self == other or self > other  # type: ignore


# Subclasses to specify a specific subtype. Usually not needed


class Int4Multirange(Multirange[int]):
    pass


class Int8Multirange(Multirange[int]):
    pass


class NumericMultirange(Multirange[Decimal]):
    pass


class DateMultirange(Multirange[date]):
    pass


class TimestampMultirange(Multirange[datetime]):
    pass


class TimestamptzMultirange(Multirange[datetime]):
    pass


class BaseMultirangeDumper(RecursiveDumper):
    def __init__(self, cls: type, context: AdaptContext | None = None):
        super().__init__(cls, context)
        self.sub_dumper: Dumper | None = None
        self._adapt_format = PyFormat.from_pq(self.format)

    def get_key(self, obj: Multirange[Any], format: PyFormat) -> DumperKey:
        # If we are a subclass whose oid is specified we don't need upgrade
        if self.cls is not Multirange:
            return self.cls

        item = self._get_item(obj)
        if item is not None:
            sd = self._tx.get_dumper(item, self._adapt_format)
            return (self.cls, sd.get_key(item, format))
        else:
            return (self.cls,)

    def upgrade(self, obj: Multirange[Any], format: PyFormat) -> BaseMultirangeDumper:
        # If we are a subclass whose oid is specified we don't need upgrade
        if self.cls is not Multirange:
            return self

        item = self._get_item(obj)
        if item is None:
            return self

        dumper: BaseMultirangeDumper
        if type(item) is int:
            # postgres won't cast int4range -> int8range so we must use
            # text format and unknown oid here
            sd = self._tx.get_dumper(item, PyFormat.TEXT)
            dumper = MultirangeDumper(self.cls, self._tx)
            dumper.sub_dumper = sd
            dumper.oid = INVALID_OID
            return dumper

        sd = self._tx.get_dumper(item, format)
        dumper = type(self)(self.cls, self._tx)
        dumper.sub_dumper = sd
        if sd.oid == INVALID_OID and isinstance(item, str):
            # Work around the normal mapping where text is dumped as unknown
            dumper.oid = self._get_multirange_oid(TEXT_OID)
        else:
            dumper.oid = self._get_multirange_oid(sd.oid)

        return dumper

    def _get_item(self, obj: Multirange[Any]) -> Any:
        """
        Return a member representative of the multirange
        """
        for r in obj:
            if r.lower is not None:
                return r.lower
            if r.upper is not None:
                return r.upper
        return None

    def _get_multirange_oid(self, sub_oid: int) -> int:
        """
        Return the oid of the range from the oid of its elements.
        """
        info = self._tx.adapters.types.get_by_subtype(MultirangeInfo, sub_oid)
        return info.oid if info else INVALID_OID


class MultirangeDumper(BaseMultirangeDumper):
    """
    Dumper for multirange types.

    The dumper can upgrade to one specific for a different range type.
    """

    def dump(self, obj: Multirange[Any]) -> Buffer | None:
        if not obj:
            return b"{}"

        item = self._get_item(obj)
        if item is not None:
            dump = self._tx.get_dumper(item, self._adapt_format).dump
        else:
            dump = fail_dump

        out: list[Buffer] = [b"{"]
        for r in obj:
            out.append(dump_range_text(r, dump))
            out.append(b",")
        out[-1] = b"}"
        return b"".join(out)


class MultirangeBinaryDumper(BaseMultirangeDumper):
    format = Format.BINARY

    def dump(self, obj: Multirange[Any]) -> Buffer | None:
        item = self._get_item(obj)
        if item is not None:
            dump = self._tx.get_dumper(item, self._adapt_format).dump
        else:
            dump = fail_dump

        out: list[Buffer] = [pack_len(len(obj))]
        for r in obj:
            data = dump_range_binary(r, dump)
            out.append(pack_len(len(data)))
            out.append(data)
        return b"".join(out)


class BaseMultirangeLoader(RecursiveLoader, Generic[T]):
    subtype_oid: int

    def __init__(self, oid: int, context: AdaptContext | None = None):
        super().__init__(oid, context)
        self._load = self._tx.get_loader(self.subtype_oid, format=self.format).load


class MultirangeLoader(BaseMultirangeLoader[T]):
    def load(self, data: Buffer) -> Multirange[T]:
        if not data or data[0] != _START_INT:
            raise e.DataError(
                "malformed multirange starting with"
                f" {bytes(data[:1]).decode('utf8', 'replace')}"
            )

        out = Multirange[T]()
        if data == b"{}":
            return out

        pos = 1
        data = data[pos:]
        try:
            while True:
                r, pos = load_range_text(data, self._load)
                out.append(r)

                sep = data[pos]  # can raise IndexError
                if sep == _SEP_INT:
                    data = data[pos + 1 :]
                    continue
                elif sep == _END_INT:
                    if len(data) == pos + 1:
                        return out
                    else:
                        raise e.DataError(
                            "malformed multirange: data after closing brace"
                        )
                else:
                    raise e.DataError(
                        f"malformed multirange: found unexpected {chr(sep)}"
                    )

        except IndexError:
            raise e.DataError("malformed multirange: separator missing")

        return out


_SEP_INT = ord(",")
_START_INT = ord("{")
_END_INT = ord("}")


class MultirangeBinaryLoader(BaseMultirangeLoader[T]):
    format = Format.BINARY

    def load(self, data: Buffer) -> Multirange[T]:
        nelems = unpack_len(data, 0)[0]
        pos = 4
        out = Multirange[T]()
        for i in range(nelems):
            length = unpack_len(data, pos)[0]
            pos += 4
            out.append(load_range_binary(data[pos : pos + length], self._load))
            pos += length

        if pos != len(data):
            raise e.DataError("unexpected trailing data in multirange")

        return out


def register_multirange(
    info: MultirangeInfo, context: AdaptContext | None = None
) -> None:
    """Register the adapters to load and dump a multirange type.

    :param info: The object with the information about the range to register.
    :param context: The context where to register the adapters. If `!None`,
        register it globally.

    Register loaders so that loading data of this type will result in a `Range`
    with bounds parsed as the right subtype.

    .. note::

        Registering the adapters doesn't affect objects already created, even
        if they are children of the registered context. For instance,
        registering the adapter globally doesn't affect already existing
        connections.
    """
    # A friendly error warning instead of an AttributeError in case fetch()
    # failed and it wasn't noticed.
    if not info:
        raise TypeError("no info passed. Is the requested multirange available?")

    # Register arrays and type info
    info.register(context)

    adapters = context.adapters if context else postgres.adapters

    # generate and register a customized text loader
    loader: type[BaseMultirangeLoader[Any]]
    loader = _make_loader(info.name, info.subtype_oid)
    adapters.register_loader(info.oid, loader)

    # generate and register a customized binary loader
    loader = _make_binary_loader(info.name, info.subtype_oid)
    adapters.register_loader(info.oid, loader)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_loader(name: str, oid: int) -> type[MultirangeLoader[Any]]:
    return type(f"{name.title()}Loader", (MultirangeLoader,), {"subtype_oid": oid})


@cache
def _make_binary_loader(name: str, oid: int) -> type[MultirangeBinaryLoader[Any]]:
    return type(
        f"{name.title()}BinaryLoader", (MultirangeBinaryLoader,), {"subtype_oid": oid}
    )


# Text dumpers for builtin multirange types wrappers
# These are registered on specific subtypes so that the upgrade mechanism
# doesn't kick in.


class Int4MultirangeDumper(MultirangeDumper):
    oid = _oids.INT4MULTIRANGE_OID


class Int8MultirangeDumper(MultirangeDumper):
    oid = _oids.INT8MULTIRANGE_OID


class NumericMultirangeDumper(MultirangeDumper):
    oid = _oids.NUMMULTIRANGE_OID


class DateMultirangeDumper(MultirangeDumper):
    oid = _oids.DATEMULTIRANGE_OID


class TimestampMultirangeDumper(MultirangeDumper):
    oid = _oids.TSMULTIRANGE_OID


class TimestamptzMultirangeDumper(MultirangeDumper):
    oid = _oids.TSTZMULTIRANGE_OID


# Binary dumpers for builtin multirange types wrappers
# These are registered on specific subtypes so that the upgrade mechanism
# doesn't kick in.


class Int4MultirangeBinaryDumper(MultirangeBinaryDumper):
    oid = _oids.INT4MULTIRANGE_OID


class Int8MultirangeBinaryDumper(MultirangeBinaryDumper):
    oid = _oids.INT8MULTIRANGE_OID


class NumericMultirangeBinaryDumper(MultirangeBinaryDumper):
    oid = _oids.NUMMULTIRANGE_OID


class DateMultirangeBinaryDumper(MultirangeBinaryDumper):
    oid = _oids.DATEMULTIRANGE_OID


class TimestampMultirangeBinaryDumper(MultirangeBinaryDumper):
    oid = _oids.TSMULTIRANGE_OID


class TimestamptzMultirangeBinaryDumper(MultirangeBinaryDumper):
    oid = _oids.TSTZMULTIRANGE_OID


# Text loaders for builtin multirange types


class Int4MultirangeLoader(MultirangeLoader[int]):
    subtype_oid = _oids.INT4_OID


class Int8MultirangeLoader(MultirangeLoader[int]):
    subtype_oid = _oids.INT8_OID


class NumericMultirangeLoader(MultirangeLoader[Decimal]):
    subtype_oid = _oids.NUMERIC_OID


class DateMultirangeLoader(MultirangeLoader[date]):
    subtype_oid = _oids.DATE_OID


class TimestampMultirangeLoader(MultirangeLoader[datetime]):
    subtype_oid = _oids.TIMESTAMP_OID


class TimestampTZMultirangeLoader(MultirangeLoader[datetime]):
    subtype_oid = _oids.TIMESTAMPTZ_OID


# Binary loaders for builtin multirange types


class Int4MultirangeBinaryLoader(MultirangeBinaryLoader[int]):
    subtype_oid = _oids.INT4_OID


class Int8MultirangeBinaryLoader(MultirangeBinaryLoader[int]):
    subtype_oid = _oids.INT8_OID


class NumericMultirangeBinaryLoader(MultirangeBinaryLoader[Decimal]):
    subtype_oid = _oids.NUMERIC_OID


class DateMultirangeBinaryLoader(MultirangeBinaryLoader[date]):
    subtype_oid = _oids.DATE_OID


class TimestampMultirangeBinaryLoader(MultirangeBinaryLoader[datetime]):
    subtype_oid = _oids.TIMESTAMP_OID


class TimestampTZMultirangeBinaryLoader(MultirangeBinaryLoader[datetime]):
    subtype_oid = _oids.TIMESTAMPTZ_OID


def register_default_adapters(context: AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper(Multirange, MultirangeBinaryDumper)
    adapters.register_dumper(Multirange, MultirangeDumper)
    adapters.register_dumper(Int4Multirange, Int4MultirangeDumper)
    adapters.register_dumper(Int8Multirange, Int8MultirangeDumper)
    adapters.register_dumper(NumericMultirange, NumericMultirangeDumper)
    adapters.register_dumper(DateMultirange, DateMultirangeDumper)
    adapters.register_dumper(TimestampMultirange, TimestampMultirangeDumper)
    adapters.register_dumper(TimestamptzMultirange, TimestamptzMultirangeDumper)
    adapters.register_dumper(Int4Multirange, Int4MultirangeBinaryDumper)
    adapters.register_dumper(Int8Multirange, Int8MultirangeBinaryDumper)
    adapters.register_dumper(NumericMultirange, NumericMultirangeBinaryDumper)
    adapters.register_dumper(DateMultirange, DateMultirangeBinaryDumper)
    adapters.register_dumper(TimestampMultirange, TimestampMultirangeBinaryDumper)
    adapters.register_dumper(TimestamptzMultirange, TimestamptzMultirangeBinaryDumper)
    adapters.register_loader("int4multirange", Int4MultirangeLoader)
    adapters.register_loader("int8multirange", Int8MultirangeLoader)
    adapters.register_loader("nummultirange", NumericMultirangeLoader)
    adapters.register_loader("datemultirange", DateMultirangeLoader)
    adapters.register_loader("tsmultirange", TimestampMultirangeLoader)
    adapters.register_loader("tstzmultirange", TimestampTZMultirangeLoader)
    adapters.register_loader("int4multirange", Int4MultirangeBinaryLoader)
    adapters.register_loader("int8multirange", Int8MultirangeBinaryLoader)
    adapters.register_loader("nummultirange", NumericMultirangeBinaryLoader)
    adapters.register_loader("datemultirange", DateMultirangeBinaryLoader)
    adapters.register_loader("tsmultirange", TimestampMultirangeBinaryLoader)
    adapters.register_loader("tstzmultirange", TimestampTZMultirangeBinaryLoader)
