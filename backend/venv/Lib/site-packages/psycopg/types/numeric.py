"""
Adapters for numeric types.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import sys
import struct
from abc import ABC, abstractmethod
from math import log
from typing import TYPE_CHECKING, Any, Callable, DefaultDict, cast
from decimal import Context, Decimal, DefaultContext

from .. import _oids
from .. import errors as e
from ..pq import Format
from ..abc import AdaptContext
from ..adapt import Buffer, Dumper, Loader, PyFormat
from .._struct import pack_float4, pack_float8, pack_int2, pack_int4, pack_int8
from .._struct import pack_uint2, pack_uint4, unpack_float4, unpack_float8, unpack_int2
from .._struct import unpack_int4, unpack_int8, unpack_uint4

# Exposed here
from .._wrappers import Float4 as Float4
from .._wrappers import Float8 as Float8
from .._wrappers import Int2 as Int2
from .._wrappers import Int4 as Int4
from .._wrappers import Int8 as Int8
from .._wrappers import IntNumeric as IntNumeric
from .._wrappers import Oid as Oid

if TYPE_CHECKING:
    import numpy


class _IntDumper(Dumper):
    def dump(self, obj: Any) -> Buffer | None:
        return str(obj).encode()

    def quote(self, obj: Any) -> Buffer:
        value = self.dump(obj)
        if value is None:
            return b"NULL"
        return value if obj >= 0 else b" " + value


class _IntOrSubclassDumper(_IntDumper):
    def dump(self, obj: Any) -> Buffer | None:
        t = type(obj)
        # Convert to int in order to dump IntEnum or numpy.integer correctly
        if t is not int:
            obj = int(obj)

        return str(obj).encode()


class _SpecialValuesDumper(Dumper):
    _special: dict[bytes, bytes] = {}

    def dump(self, obj: Any) -> Buffer | None:
        return str(obj).encode()

    def quote(self, obj: Any) -> Buffer:
        value = self.dump(obj)

        if value is None:
            return b"NULL"
        if not isinstance(value, bytes):
            value = bytes(value)
        if value in self._special:
            return self._special[value]

        return value if obj >= 0 else b" " + value


class FloatDumper(_SpecialValuesDumper):
    oid = _oids.FLOAT8_OID

    _special = {
        b"inf": b"'Infinity'::float8",
        b"-inf": b"'-Infinity'::float8",
        b"nan": b"'NaN'::float8",
    }


class Float4Dumper(FloatDumper):
    oid = _oids.FLOAT4_OID


class FloatBinaryDumper(Dumper):
    format = Format.BINARY
    oid = _oids.FLOAT8_OID

    def dump(self, obj: float) -> Buffer | None:
        return pack_float8(obj)


class Float4BinaryDumper(FloatBinaryDumper):
    oid = _oids.FLOAT4_OID

    def dump(self, obj: float) -> Buffer | None:
        return pack_float4(obj)


class DecimalDumper(_SpecialValuesDumper):
    oid = _oids.NUMERIC_OID

    def dump(self, obj: Decimal) -> Buffer | None:
        return dump_decimal_to_text(obj)

    _special = {
        b"Infinity": b"'Infinity'::numeric",
        b"-Infinity": b"'-Infinity'::numeric",
        b"NaN": b"'NaN'::numeric",
    }


class Int2Dumper(_IntOrSubclassDumper):
    oid = _oids.INT2_OID


class Int4Dumper(_IntOrSubclassDumper):
    oid = _oids.INT4_OID


class Int8Dumper(_IntOrSubclassDumper):
    oid = _oids.INT8_OID


class IntNumericDumper(_IntOrSubclassDumper):
    oid = _oids.NUMERIC_OID


class OidDumper(_IntOrSubclassDumper):
    oid = _oids.OID_OID


class IntDumper(Dumper):
    def dump(self, obj: Any) -> Buffer | None:
        raise TypeError(
            f"{type(self).__name__} is a dispatcher to other dumpers:"
            " dump() is not supposed to be called"
        )

    def get_key(self, obj: int, format: PyFormat) -> type:
        return self.upgrade(obj, format).cls

    _int2_dumper = Int2Dumper(Int2)
    _int4_dumper = Int4Dumper(Int4)
    _int8_dumper = Int8Dumper(Int8)
    _int_numeric_dumper = IntNumericDumper(IntNumeric)

    def upgrade(self, obj: int, format: PyFormat) -> Dumper:
        if -(2**31) <= obj < 2**31:
            if -(2**15) <= obj < 2**15:
                return self._int2_dumper
            else:
                return self._int4_dumper
        else:
            if -(2**63) <= obj < 2**63:
                return self._int8_dumper
            else:
                return self._int_numeric_dumper


class Int2BinaryDumper(Int2Dumper):
    format = Format.BINARY

    def dump(self, obj: int) -> Buffer | None:
        return pack_int2(obj)


class Int4BinaryDumper(Int4Dumper):
    format = Format.BINARY

    def dump(self, obj: int) -> Buffer | None:
        return pack_int4(obj)


class Int8BinaryDumper(Int8Dumper):
    format = Format.BINARY

    def dump(self, obj: int) -> Buffer | None:
        return pack_int8(obj)


# Ratio between number of bits required to store a number and number of pg
# decimal digits required.
BIT_PER_PGDIGIT = log(2) / log(10_000)


class IntNumericBinaryDumper(IntNumericDumper):
    format = Format.BINARY

    def dump(self, obj: int) -> Buffer | None:
        return dump_int_to_numeric_binary(obj)


class OidBinaryDumper(OidDumper):
    format = Format.BINARY

    def dump(self, obj: int) -> Buffer | None:
        return pack_uint4(obj)


class IntBinaryDumper(IntDumper):
    format = Format.BINARY

    _int2_dumper = Int2BinaryDumper(Int2)
    _int4_dumper = Int4BinaryDumper(Int4)
    _int8_dumper = Int8BinaryDumper(Int8)
    _int_numeric_dumper = IntNumericBinaryDumper(IntNumeric)


class IntLoader(Loader):
    def load(self, data: Buffer) -> int:
        # it supports bytes directly
        return int(data)


class Int2BinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> int:
        return unpack_int2(data)[0]


class Int4BinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> int:
        return unpack_int4(data)[0]


class Int8BinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> int:
        return unpack_int8(data)[0]


class OidBinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> int:
        return unpack_uint4(data)[0]


class FloatLoader(Loader):
    def load(self, data: Buffer) -> float:
        # it supports bytes directly
        return float(data)


class Float4BinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> float:
        return unpack_float4(data)[0]


class Float8BinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> float:
        return unpack_float8(data)[0]


class NumericLoader(Loader):
    def load(self, data: Buffer) -> Decimal:
        if isinstance(data, memoryview):
            data = bytes(data)
        return Decimal(data.decode())


DEC_DIGITS = 4  # decimal digits per Postgres "digit"
NUMERIC_POS = 0x0000
NUMERIC_NEG = 0x4000
NUMERIC_NAN = 0xC000
NUMERIC_PINF = 0xD000
NUMERIC_NINF = 0xF000

_decimal_special = {
    NUMERIC_NAN: Decimal("NaN"),
    NUMERIC_PINF: Decimal("Infinity"),
    NUMERIC_NINF: Decimal("-Infinity"),
}


class _ContextMap(DefaultDict[int, Context]):
    """
    Cache for decimal contexts to use when the precision requires it.

    Note: if the default context is used (prec=28) you can get an invalid
    operation or a rounding to 0:

    - Decimal(1000).shift(24) = Decimal('1000000000000000000000000000')
    - Decimal(1000).shift(25) = Decimal('0')
    - Decimal(1000).shift(30) raises InvalidOperation
    """

    def __missing__(self, key: int) -> Context:
        val = Context(prec=key)
        self[key] = val
        return val


_contexts = _ContextMap()
for i in range(DefaultContext.prec):
    _contexts[i] = DefaultContext

_unpack_numeric_head = cast(
    Callable[[Buffer], "tuple[int, int, int, int]"],
    struct.Struct("!HhHH").unpack_from,
)
_pack_numeric_head = cast(
    Callable[[int, int, int, int], bytes],
    struct.Struct("!HhHH").pack,
)


class NumericBinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> Decimal:
        ndigits, weight, sign, dscale = _unpack_numeric_head(data)
        if sign == NUMERIC_POS or sign == NUMERIC_NEG:
            val = 0
            for i in range(8, len(data), 2):
                val = val * 10_000 + data[i] * 0x100 + data[i + 1]

            shift = dscale - (ndigits - weight - 1) * DEC_DIGITS
            ctx = _contexts[(weight + 2) * DEC_DIGITS + dscale]
            return (
                Decimal(val if sign == NUMERIC_POS else -val)
                .scaleb(-dscale, ctx)
                .shift(shift, ctx)
            )
        else:
            try:
                return _decimal_special[sign]
            except KeyError:
                raise e.DataError(f"bad value for numeric sign: 0x{sign:X}") from None


NUMERIC_NAN_BIN = _pack_numeric_head(0, 0, NUMERIC_NAN, 0)
NUMERIC_PINF_BIN = _pack_numeric_head(0, 0, NUMERIC_PINF, 0)
NUMERIC_NINF_BIN = _pack_numeric_head(0, 0, NUMERIC_NINF, 0)


class DecimalBinaryDumper(Dumper):
    format = Format.BINARY
    oid = _oids.NUMERIC_OID

    def dump(self, obj: Decimal) -> Buffer | None:
        return dump_decimal_to_numeric_binary(obj)


class _MixedNumericDumper(Dumper, ABC):
    """Base for dumper to dump int, decimal, numpy.integer to Postgres numeric

    Only used when looking up by oid.
    """

    oid = _oids.NUMERIC_OID

    # If numpy is available, the dumped object might be a numpy integer too
    int_classes: type | tuple[type, ...] = ()

    def __init__(self, cls: type, context: AdaptContext | None = None):
        super().__init__(cls, context)

        # Verify if numpy is available. If it is, we might have to dump
        # its integers too.
        if not _MixedNumericDumper.int_classes:
            if "numpy" in sys.modules:
                import numpy

                _MixedNumericDumper.int_classes = (int, numpy.integer)
            else:
                _MixedNumericDumper.int_classes = int

    @abstractmethod
    def dump(self, obj: Decimal | int | numpy.integer[Any]) -> Buffer | None: ...


class NumericDumper(_MixedNumericDumper):
    def dump(self, obj: Decimal | int | numpy.integer[Any]) -> Buffer | None:
        if isinstance(obj, self.int_classes):
            return str(obj).encode()
        elif isinstance(obj, Decimal):
            return dump_decimal_to_text(obj)
        else:
            raise TypeError(
                f"class {type(self).__name__} cannot dump {type(obj).__name__}"
            )


class NumericBinaryDumper(_MixedNumericDumper):
    format = Format.BINARY

    def dump(self, obj: Decimal | int | numpy.integer[Any]) -> Buffer | None:
        if type(obj) is int:
            return dump_int_to_numeric_binary(obj)
        elif isinstance(obj, Decimal):
            return dump_decimal_to_numeric_binary(obj)
        elif isinstance(obj, self.int_classes):
            return dump_int_to_numeric_binary(int(obj))
        else:
            raise TypeError(
                f"class {type(self).__name__} cannot dump {type(obj).__name__}"
            )


def dump_decimal_to_text(obj: Decimal) -> bytes:
    if obj.is_nan():
        # cover NaN and sNaN
        return b"NaN"
    else:
        return str(obj).encode()


def dump_decimal_to_numeric_binary(obj: Decimal) -> bytearray | bytes:
    sign, digits, exp = obj.as_tuple()
    if exp == "n" or exp == "N":
        return NUMERIC_NAN_BIN
    elif exp == "F":
        return NUMERIC_NINF_BIN if sign else NUMERIC_PINF_BIN

    # Weights of py digits into a pg digit according to their positions.
    # Starting with an index wi != 0 is equivalent to prepending 0's to
    # the digits tuple, but without really changing it.
    weights = (1000, 100, 10, 1)
    wi = 0

    ndigits = nzdigits = len(digits)

    # Find the last nonzero digit
    while nzdigits > 0 and digits[nzdigits - 1] == 0:
        nzdigits -= 1

    if exp <= 0:
        dscale = -exp
    else:
        dscale = 0
        # align the py digits to the pg digits if there's some py exponent
        ndigits += exp % DEC_DIGITS

    if not nzdigits:
        return _pack_numeric_head(0, 0, NUMERIC_POS, dscale)

    # Equivalent of 0-padding left to align the py digits to the pg digits
    # but without changing the digits tuple.
    mod = (ndigits - dscale) % DEC_DIGITS
    if mod:
        wi = DEC_DIGITS - mod
        ndigits += wi

    tmp = nzdigits + wi
    out = bytearray(
        _pack_numeric_head(
            tmp // DEC_DIGITS + (tmp % DEC_DIGITS and 1),  # ndigits
            (ndigits + exp) // DEC_DIGITS - 1,  # weight
            NUMERIC_NEG if sign else NUMERIC_POS,  # sign
            dscale,
        )
    )

    pgdigit = 0
    for i in range(nzdigits):
        pgdigit += weights[wi] * digits[i]
        wi += 1
        if wi >= DEC_DIGITS:
            out += pack_uint2(pgdigit)
            pgdigit = wi = 0

    if pgdigit:
        out += pack_uint2(pgdigit)

    return out


def dump_int_to_numeric_binary(obj: int) -> bytearray:
    ndigits = int(obj.bit_length() * BIT_PER_PGDIGIT) + 1
    out = bytearray(b"\x00\x00" * (ndigits + 4))
    if obj < 0:
        sign = NUMERIC_NEG
        obj = -obj
    else:
        sign = NUMERIC_POS

    out[:8] = _pack_numeric_head(ndigits, ndigits - 1, sign, 0)
    i = 8 + (ndigits - 1) * 2
    while obj:
        rem = obj % 10_000
        obj //= 10_000
        out[i : i + 2] = pack_uint2(rem)
        i -= 2

    return out


def register_default_adapters(context: AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper(int, IntDumper)
    adapters.register_dumper(int, IntBinaryDumper)
    adapters.register_dumper(float, FloatDumper)
    adapters.register_dumper(float, FloatBinaryDumper)
    adapters.register_dumper(Int2, Int2Dumper)
    adapters.register_dumper(Int4, Int4Dumper)
    adapters.register_dumper(Int8, Int8Dumper)
    adapters.register_dumper(IntNumeric, IntNumericDumper)
    adapters.register_dumper(Oid, OidDumper)

    # The binary dumper is currently some 30% slower, so default to text
    # (see tests/scripts/testdec.py for a rough benchmark)
    # Also, must be after IntNumericDumper
    adapters.register_dumper("decimal.Decimal", DecimalBinaryDumper)
    adapters.register_dumper("decimal.Decimal", DecimalDumper)

    # Used only by oid, can take both int and Decimal as input
    adapters.register_dumper(None, NumericBinaryDumper)
    adapters.register_dumper(None, NumericDumper)

    adapters.register_dumper(Float4, Float4Dumper)
    adapters.register_dumper(Float8, FloatDumper)
    adapters.register_dumper(Int2, Int2BinaryDumper)
    adapters.register_dumper(Int4, Int4BinaryDumper)
    adapters.register_dumper(Int8, Int8BinaryDumper)
    adapters.register_dumper(Oid, OidBinaryDumper)
    adapters.register_dumper(Float4, Float4BinaryDumper)
    adapters.register_dumper(Float8, FloatBinaryDumper)
    adapters.register_loader("int2", IntLoader)
    adapters.register_loader("int4", IntLoader)
    adapters.register_loader("int8", IntLoader)
    adapters.register_loader("oid", IntLoader)
    adapters.register_loader("int2", Int2BinaryLoader)
    adapters.register_loader("int4", Int4BinaryLoader)
    adapters.register_loader("int8", Int8BinaryLoader)
    adapters.register_loader("oid", OidBinaryLoader)
    adapters.register_loader("float4", FloatLoader)
    adapters.register_loader("float8", FloatLoader)
    adapters.register_loader("float4", Float4BinaryLoader)
    adapters.register_loader("float8", Float8BinaryLoader)
    adapters.register_loader("numeric", NumericLoader)
    adapters.register_loader("numeric", NumericBinaryLoader)
