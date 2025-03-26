"""
Support for range types adaptation.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Generic, cast
from decimal import Decimal
from datetime import date, datetime

from .. import _oids
from .. import errors as e
from .. import postgres, sql
from ..pq import Format
from ..abc import AdaptContext, Buffer, Dumper, DumperKey, DumpFunc, LoadFunc, Query
from .._oids import INVALID_OID, TEXT_OID
from ..adapt import PyFormat, RecursiveDumper, RecursiveLoader
from .._compat import TypeVar, cache
from .._struct import pack_len, unpack_len
from .._typeinfo import TypeInfo, TypesRegistry

if TYPE_CHECKING:
    from .._connection_base import BaseConnection

RANGE_EMPTY = 0x01  # range is empty
RANGE_LB_INC = 0x02  # lower bound is inclusive
RANGE_UB_INC = 0x04  # upper bound is inclusive
RANGE_LB_INF = 0x08  # lower bound is -infinity
RANGE_UB_INF = 0x10  # upper bound is +infinity

_EMPTY_HEAD = bytes([RANGE_EMPTY])

T = TypeVar("T")


class RangeInfo(TypeInfo):
    """Manage information about a range type."""

    def __init__(
        self,
        name: str,
        oid: int,
        array_oid: int,
        *,
        regtype: str = "",
        subtype_oid: int,
    ):
        super().__init__(name, oid, array_oid, regtype=regtype)
        self.subtype_oid = subtype_oid

    @classmethod
    def _get_info_query(cls, conn: BaseConnection[Any]) -> Query:
        return sql.SQL(
            """\
SELECT t.typname AS name, t.oid AS oid, t.typarray AS array_oid,
    t.oid::regtype::text AS regtype,
    r.rngsubtype AS subtype_oid
FROM pg_type t
JOIN pg_range r ON t.oid = r.rngtypid
WHERE t.oid = {regtype}
"""
        ).format(regtype=cls._to_regtype(conn))

    def _added(self, registry: TypesRegistry) -> None:
        # Map ranges subtypes to info
        registry._registry[RangeInfo, self.subtype_oid] = self


class Range(Generic[T]):
    """Python representation for a PostgreSQL range type.

    :param lower: lower bound for the range. `!None` means unbound
    :param upper: upper bound for the range. `!None` means unbound
    :param bounds: one of the literal strings ``()``, ``[)``, ``(]``, ``[]``,
        representing whether the lower or upper bounds are included
    :param empty: if `!True`, the range is empty

    """

    __slots__ = ("_lower", "_upper", "_bounds")

    def __init__(
        self,
        lower: T | None = None,
        upper: T | None = None,
        bounds: str = "[)",
        empty: bool = False,
    ):
        if not empty:
            if bounds not in ("[)", "(]", "()", "[]"):
                raise ValueError("bound flags not valid: %r" % bounds)

            self._lower = lower
            self._upper = upper

            # Make bounds consistent with infs
            if lower is None and bounds[0] == "[":
                bounds = "(" + bounds[1]
            if upper is None and bounds[1] == "]":
                bounds = bounds[0] + ")"

            self._bounds = bounds
        else:
            self._lower = self._upper = None
            self._bounds = ""

    def __repr__(self) -> str:
        if self._bounds:
            args = f"{self._lower!r}, {self._upper!r}, {self._bounds!r}"
        else:
            args = "empty=True"

        return f"{self.__class__.__name__}({args})"

    def __str__(self) -> str:
        if not self._bounds:
            return "empty"

        items = [
            self._bounds[0],
            str(self._lower),
            ", ",
            str(self._upper),
            self._bounds[1],
        ]
        return "".join(items)

    @property
    def lower(self) -> T | None:
        """The lower bound of the range. `!None` if empty or unbound."""
        return self._lower

    @property
    def upper(self) -> T | None:
        """The upper bound of the range. `!None` if empty or unbound."""
        return self._upper

    @property
    def bounds(self) -> str:
        """The bounds string (two characters from '[', '(', ']', ')')."""
        return self._bounds

    @property
    def isempty(self) -> bool:
        """`!True` if the range is empty."""
        return not self._bounds

    @property
    def lower_inf(self) -> bool:
        """`!True` if the range doesn't have a lower bound."""
        if not self._bounds:
            return False
        return self._lower is None

    @property
    def upper_inf(self) -> bool:
        """`!True` if the range doesn't have an upper bound."""
        if not self._bounds:
            return False
        return self._upper is None

    @property
    def lower_inc(self) -> bool:
        """`!True` if the lower bound is included in the range."""
        if not self._bounds or self._lower is None:
            return False
        return self._bounds[0] == "["

    @property
    def upper_inc(self) -> bool:
        """`!True` if the upper bound is included in the range."""
        if not self._bounds or self._upper is None:
            return False
        return self._bounds[1] == "]"

    def __contains__(self, x: T) -> bool:
        if not self._bounds:
            return False

        if self._lower is not None:
            if self._bounds[0] == "[":
                # It doesn't seem that Python has an ABC for ordered types.
                if x < self._lower:  # type: ignore[operator]
                    return False
            else:
                if x <= self._lower:  # type: ignore[operator]
                    return False

        if self._upper is not None:
            if self._bounds[1] == "]":
                if x > self._upper:  # type: ignore[operator]
                    return False
            else:
                if x >= self._upper:  # type: ignore[operator]
                    return False

        return True

    def __bool__(self) -> bool:
        return bool(self._bounds)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Range):
            return False
        return (
            self._lower == other._lower
            and self._upper == other._upper
            and self._bounds == other._bounds
        )

    def __hash__(self) -> int:
        return hash((self._lower, self._upper, self._bounds))

    # as the postgres docs describe for the server-side stuff,
    # ordering is rather arbitrary, but will remain stable
    # and consistent.

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Range):
            return NotImplemented
        for attr in ("_lower", "_upper", "_bounds"):
            self_value = getattr(self, attr)
            other_value = getattr(other, attr)
            if self_value == other_value:
                pass
            elif self_value is None:
                return True
            elif other_value is None:
                return False
            else:
                return cast(bool, self_value < other_value)
        return False

    def __le__(self, other: Any) -> bool:
        return self == other or self < other  # type: ignore

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Range):
            return other < self
        else:
            return NotImplemented

    def __ge__(self, other: Any) -> bool:
        return self == other or self > other  # type: ignore

    def __getstate__(self) -> dict[str, Any]:
        return {
            slot: getattr(self, slot) for slot in self.__slots__ if hasattr(self, slot)
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        for slot, value in state.items():
            setattr(self, slot, value)


# Subclasses to specify a specific subtype. Usually not needed: only needed
# in binary copy, where switching to text is not an option.


class Int4Range(Range[int]):
    pass


class Int8Range(Range[int]):
    pass


class NumericRange(Range[Decimal]):
    pass


class DateRange(Range[date]):
    pass


class TimestampRange(Range[datetime]):
    pass


class TimestamptzRange(Range[datetime]):
    pass


class BaseRangeDumper(RecursiveDumper):
    def __init__(self, cls: type, context: AdaptContext | None = None):
        super().__init__(cls, context)
        self.sub_dumper: Dumper | None = None
        self._adapt_format = PyFormat.from_pq(self.format)

    def get_key(self, obj: Range[Any], format: PyFormat) -> DumperKey:
        # If we are a subclass whose oid is specified we don't need upgrade
        if self.cls is not Range:
            return self.cls

        item = self._get_item(obj)
        if item is not None:
            sd = self._tx.get_dumper(item, self._adapt_format)
            return (self.cls, sd.get_key(item, format))
        else:
            return (self.cls,)

    def upgrade(self, obj: Range[Any], format: PyFormat) -> BaseRangeDumper:
        # If we are a subclass whose oid is specified we don't need upgrade
        if self.cls is not Range:
            return self

        item = self._get_item(obj)
        if item is None:
            return self

        dumper: BaseRangeDumper
        if type(item) is int:
            # postgres won't cast int4range -> int8range so we must use
            # text format and unknown oid here
            sd = self._tx.get_dumper(item, PyFormat.TEXT)
            dumper = RangeDumper(self.cls, self._tx)
            dumper.sub_dumper = sd
            dumper.oid = INVALID_OID
            return dumper

        sd = self._tx.get_dumper(item, format)
        dumper = type(self)(self.cls, self._tx)
        dumper.sub_dumper = sd
        if sd.oid == INVALID_OID and isinstance(item, str):
            # Work around the normal mapping where text is dumped as unknown
            dumper.oid = self._get_range_oid(TEXT_OID)
        else:
            dumper.oid = self._get_range_oid(sd.oid)

        return dumper

    def _get_item(self, obj: Range[Any]) -> Any:
        """
        Return a member representative of the range
        """
        rv = obj.lower
        return rv if rv is not None else obj.upper

    def _get_range_oid(self, sub_oid: int) -> int:
        """
        Return the oid of the range from the oid of its elements.
        """
        info = self._tx.adapters.types.get_by_subtype(RangeInfo, sub_oid)
        return info.oid if info else INVALID_OID


class RangeDumper(BaseRangeDumper):
    """
    Dumper for range types.

    The dumper can upgrade to one specific for a different range type.
    """

    def dump(self, obj: Range[Any]) -> Buffer | None:
        item = self._get_item(obj)
        if item is not None:
            dump = self._tx.get_dumper(item, self._adapt_format).dump
        else:
            dump = fail_dump

        return dump_range_text(obj, dump)


def dump_range_text(obj: Range[Any], dump: DumpFunc) -> Buffer:
    if obj.isempty:
        return b"empty"

    parts: list[Buffer] = [b"[" if obj.lower_inc else b"("]

    def dump_item(item: Any) -> Buffer:
        ad = dump(item)
        if ad is None:
            return b""
        elif not ad:
            return b'""'
        elif _re_needs_quotes.search(ad):
            return b'"' + _re_esc.sub(rb"\1\1", ad) + b'"'
        else:
            return ad

    if obj.lower is not None:
        parts.append(dump_item(obj.lower))

    parts.append(b",")

    if obj.upper is not None:
        parts.append(dump_item(obj.upper))

    parts.append(b"]" if obj.upper_inc else b")")

    return b"".join(parts)


_re_needs_quotes = re.compile(rb'[",\\\s()\[\]]')
_re_esc = re.compile(rb"([\\\"])")


class RangeBinaryDumper(BaseRangeDumper):
    format = Format.BINARY

    def dump(self, obj: Range[Any]) -> Buffer | None:
        item = self._get_item(obj)
        if item is not None:
            dump = self._tx.get_dumper(item, self._adapt_format).dump
        else:
            dump = fail_dump

        return dump_range_binary(obj, dump)


def dump_range_binary(obj: Range[Any], dump: DumpFunc) -> Buffer:
    if not obj:
        return _EMPTY_HEAD

    out = bytearray([0])  # will replace the head later

    head = 0
    if obj.lower_inc:
        head |= RANGE_LB_INC
    if obj.upper_inc:
        head |= RANGE_UB_INC

    if obj.lower is not None:
        data = dump(obj.lower)
        if data is not None:
            out += pack_len(len(data))
            out += data
        else:
            head |= RANGE_LB_INF
    else:
        head |= RANGE_LB_INF

    if obj.upper is not None:
        data = dump(obj.upper)
        if data is not None:
            out += pack_len(len(data))
            out += data
        else:
            head |= RANGE_UB_INF
    else:
        head |= RANGE_UB_INF

    out[0] = head
    return out


def fail_dump(obj: Any) -> Buffer:
    raise e.InternalError("trying to dump a range element without information")


class BaseRangeLoader(RecursiveLoader, Generic[T]):
    """Generic loader for a range.

    Subclasses must specify the oid of the subtype and the class to load.
    """

    subtype_oid: int

    def __init__(self, oid: int, context: AdaptContext | None = None):
        super().__init__(oid, context)
        self._load = self._tx.get_loader(self.subtype_oid, format=self.format).load


class RangeLoader(BaseRangeLoader[T]):
    def load(self, data: Buffer) -> Range[T]:
        return load_range_text(data, self._load)[0]


def load_range_text(data: Buffer, load: LoadFunc) -> tuple[Range[Any], int]:
    if data == b"empty":
        return Range(empty=True), 5

    m = _re_range.match(data)
    if m is None:
        raise e.DataError(
            f"failed to parse range: '{bytes(data).decode('utf8', 'replace')}'"
        )

    lower = None
    item = m.group(3)
    if item is None:
        item = m.group(2)
        if item is not None:
            lower = load(_re_undouble.sub(rb"\1", item))
    else:
        lower = load(item)

    upper = None
    item = m.group(5)
    if item is None:
        item = m.group(4)
        if item is not None:
            upper = load(_re_undouble.sub(rb"\1", item))
    else:
        upper = load(item)

    bounds = (m.group(1) + m.group(6)).decode()

    return Range(lower, upper, bounds), m.end()


_re_range = re.compile(
    rb"""
    ( \(|\[ )                   # lower bound flag
    (?:                         # lower bound:
      " ( (?: [^"] | "")* ) "   #   - a quoted string
      | ( [^",]+ )              #   - or an unquoted string
    )?                          #   - or empty (not caught)
    ,
    (?:                         # upper bound:
      " ( (?: [^"] | "")* ) "   #   - a quoted string
      | ( [^"\)\]]+ )           #   - or an unquoted string
    )?                          #   - or empty (not caught)
    ( \)|\] )                   # upper bound flag
    """,
    re.VERBOSE,
)

_re_undouble = re.compile(rb'(["\\])\1')


class RangeBinaryLoader(BaseRangeLoader[T]):
    format = Format.BINARY

    def load(self, data: Buffer) -> Range[T]:
        return load_range_binary(data, self._load)


def load_range_binary(data: Buffer, load: LoadFunc) -> Range[Any]:
    head = data[0]
    if head & RANGE_EMPTY:
        return Range(empty=True)

    lb = "[" if head & RANGE_LB_INC else "("
    ub = "]" if head & RANGE_UB_INC else ")"

    pos = 1  # after the head
    if head & RANGE_LB_INF:
        min = None
    else:
        length = unpack_len(data, pos)[0]
        pos += 4
        min = load(data[pos : pos + length])
        pos += length

    if head & RANGE_UB_INF:
        max = None
    else:
        length = unpack_len(data, pos)[0]
        pos += 4
        max = load(data[pos : pos + length])
        pos += length

    return Range(min, max, lb + ub)


def register_range(info: RangeInfo, context: AdaptContext | None = None) -> None:
    """Register the adapters to load and dump a range type.

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
        raise TypeError("no info passed. Is the requested range available?")

    # Register arrays and type info
    info.register(context)

    adapters = context.adapters if context else postgres.adapters

    # generate and register a customized text loader
    loader: type[BaseRangeLoader[Any]]
    loader = _make_loader(info.name, info.subtype_oid)
    adapters.register_loader(info.oid, loader)

    # generate and register a customized binary loader
    loader = _make_binary_loader(info.name, info.subtype_oid)
    adapters.register_loader(info.oid, loader)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_loader(name: str, oid: int) -> type[RangeLoader[Any]]:
    return type(f"{name.title()}Loader", (RangeLoader,), {"subtype_oid": oid})


@cache
def _make_binary_loader(name: str, oid: int) -> type[RangeBinaryLoader[Any]]:
    return type(
        f"{name.title()}BinaryLoader", (RangeBinaryLoader,), {"subtype_oid": oid}
    )


# Text dumpers for builtin range types wrappers
# These are registered on specific subtypes so that the upgrade mechanism
# doesn't kick in.


class Int4RangeDumper(RangeDumper):
    oid = _oids.INT4RANGE_OID


class Int8RangeDumper(RangeDumper):
    oid = _oids.INT8RANGE_OID


class NumericRangeDumper(RangeDumper):
    oid = _oids.NUMRANGE_OID


class DateRangeDumper(RangeDumper):
    oid = _oids.DATERANGE_OID


class TimestampRangeDumper(RangeDumper):
    oid = _oids.TSRANGE_OID


class TimestamptzRangeDumper(RangeDumper):
    oid = _oids.TSTZRANGE_OID


# Binary dumpers for builtin range types wrappers
# These are registered on specific subtypes so that the upgrade mechanism
# doesn't kick in.


class Int4RangeBinaryDumper(RangeBinaryDumper):
    oid = _oids.INT4RANGE_OID


class Int8RangeBinaryDumper(RangeBinaryDumper):
    oid = _oids.INT8RANGE_OID


class NumericRangeBinaryDumper(RangeBinaryDumper):
    oid = _oids.NUMRANGE_OID


class DateRangeBinaryDumper(RangeBinaryDumper):
    oid = _oids.DATERANGE_OID


class TimestampRangeBinaryDumper(RangeBinaryDumper):
    oid = _oids.TSRANGE_OID


class TimestamptzRangeBinaryDumper(RangeBinaryDumper):
    oid = _oids.TSTZRANGE_OID


# Text loaders for builtin range types


class Int4RangeLoader(RangeLoader[int]):
    subtype_oid = _oids.INT4_OID


class Int8RangeLoader(RangeLoader[int]):
    subtype_oid = _oids.INT8_OID


class NumericRangeLoader(RangeLoader[Decimal]):
    subtype_oid = _oids.NUMERIC_OID


class DateRangeLoader(RangeLoader[date]):
    subtype_oid = _oids.DATE_OID


class TimestampRangeLoader(RangeLoader[datetime]):
    subtype_oid = _oids.TIMESTAMP_OID


class TimestampTZRangeLoader(RangeLoader[datetime]):
    subtype_oid = _oids.TIMESTAMPTZ_OID


# Binary loaders for builtin range types


class Int4RangeBinaryLoader(RangeBinaryLoader[int]):
    subtype_oid = _oids.INT4_OID


class Int8RangeBinaryLoader(RangeBinaryLoader[int]):
    subtype_oid = _oids.INT8_OID


class NumericRangeBinaryLoader(RangeBinaryLoader[Decimal]):
    subtype_oid = _oids.NUMERIC_OID


class DateRangeBinaryLoader(RangeBinaryLoader[date]):
    subtype_oid = _oids.DATE_OID


class TimestampRangeBinaryLoader(RangeBinaryLoader[datetime]):
    subtype_oid = _oids.TIMESTAMP_OID


class TimestampTZRangeBinaryLoader(RangeBinaryLoader[datetime]):
    subtype_oid = _oids.TIMESTAMPTZ_OID


def register_default_adapters(context: AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper(Range, RangeBinaryDumper)
    adapters.register_dumper(Range, RangeDumper)
    adapters.register_dumper(Int4Range, Int4RangeDumper)
    adapters.register_dumper(Int8Range, Int8RangeDumper)
    adapters.register_dumper(NumericRange, NumericRangeDumper)
    adapters.register_dumper(DateRange, DateRangeDumper)
    adapters.register_dumper(TimestampRange, TimestampRangeDumper)
    adapters.register_dumper(TimestamptzRange, TimestamptzRangeDumper)
    adapters.register_dumper(Int4Range, Int4RangeBinaryDumper)
    adapters.register_dumper(Int8Range, Int8RangeBinaryDumper)
    adapters.register_dumper(NumericRange, NumericRangeBinaryDumper)
    adapters.register_dumper(DateRange, DateRangeBinaryDumper)
    adapters.register_dumper(TimestampRange, TimestampRangeBinaryDumper)
    adapters.register_dumper(TimestamptzRange, TimestamptzRangeBinaryDumper)
    adapters.register_loader("int4range", Int4RangeLoader)
    adapters.register_loader("int8range", Int8RangeLoader)
    adapters.register_loader("numrange", NumericRangeLoader)
    adapters.register_loader("daterange", DateRangeLoader)
    adapters.register_loader("tsrange", TimestampRangeLoader)
    adapters.register_loader("tstzrange", TimestampTZRangeLoader)
    adapters.register_loader("int4range", Int4RangeBinaryLoader)
    adapters.register_loader("int8range", Int8RangeBinaryLoader)
    adapters.register_loader("numrange", NumericRangeBinaryLoader)
    adapters.register_loader("daterange", DateRangeBinaryLoader)
    adapters.register_loader("tsrange", TimestampRangeBinaryLoader)
    adapters.register_loader("tstzrange", TimestampTZRangeBinaryLoader)
