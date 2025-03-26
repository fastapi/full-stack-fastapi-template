"""
Adapters for numpy types.
"""

# Copyright (C) 2022 The Psycopg Team

from typing import Any

from .. import _oids
from ..pq import Format
from ..abc import AdaptContext, Buffer
from .bool import BoolBinaryDumper, BoolDumper
from .numeric import Float4BinaryDumper, Float4Dumper, FloatBinaryDumper, FloatDumper
from .numeric import _IntDumper, dump_int_to_numeric_binary
from .._struct import pack_int2, pack_int4, pack_int8


class NPInt16Dumper(_IntDumper):
    oid = _oids.INT2_OID


class NPInt32Dumper(_IntDumper):
    oid = _oids.INT4_OID


class NPInt64Dumper(_IntDumper):
    oid = _oids.INT8_OID


class NPNumericDumper(_IntDumper):
    oid = _oids.NUMERIC_OID


# Binary Dumpers


class NPInt16BinaryDumper(NPInt16Dumper):
    format = Format.BINARY

    def dump(self, obj: Any) -> bytes:
        return pack_int2(int(obj))


class NPInt32BinaryDumper(NPInt32Dumper):
    format = Format.BINARY

    def dump(self, obj: Any) -> bytes:
        return pack_int4(int(obj))


class NPInt64BinaryDumper(NPInt64Dumper):
    format = Format.BINARY

    def dump(self, obj: Any) -> bytes:
        return pack_int8(int(obj))


class NPNumericBinaryDumper(NPNumericDumper):
    format = Format.BINARY

    def dump(self, obj: Any) -> Buffer:
        return dump_int_to_numeric_binary(int(obj))


def register_default_adapters(context: AdaptContext) -> None:
    adapters = context.adapters

    adapters.register_dumper("numpy.int8", NPInt16Dumper)
    adapters.register_dumper("numpy.int16", NPInt16Dumper)
    adapters.register_dumper("numpy.int32", NPInt32Dumper)
    adapters.register_dumper("numpy.int64", NPInt64Dumper)
    adapters.register_dumper("numpy.longlong", NPInt64Dumper)
    adapters.register_dumper("numpy.bool", BoolDumper)
    adapters.register_dumper("numpy.bool_", BoolDumper)
    adapters.register_dumper("numpy.uint8", NPInt16Dumper)
    adapters.register_dumper("numpy.uint16", NPInt32Dumper)
    adapters.register_dumper("numpy.uint32", NPInt64Dumper)
    adapters.register_dumper("numpy.uint64", NPNumericDumper)
    adapters.register_dumper("numpy.ulonglong", NPNumericDumper)
    adapters.register_dumper("numpy.float16", Float4Dumper)
    adapters.register_dumper("numpy.float32", Float4Dumper)
    adapters.register_dumper("numpy.float64", FloatDumper)

    adapters.register_dumper("numpy.int8", NPInt16BinaryDumper)
    adapters.register_dumper("numpy.int16", NPInt16BinaryDumper)
    adapters.register_dumper("numpy.int32", NPInt32BinaryDumper)
    adapters.register_dumper("numpy.int64", NPInt64BinaryDumper)
    adapters.register_dumper("numpy.longlong", NPInt64BinaryDumper)
    adapters.register_dumper("numpy.bool", BoolBinaryDumper)
    adapters.register_dumper("numpy.bool_", BoolBinaryDumper)
    adapters.register_dumper("numpy.uint8", NPInt16BinaryDumper)
    adapters.register_dumper("numpy.uint16", NPInt32BinaryDumper)
    adapters.register_dumper("numpy.uint32", NPInt64BinaryDumper)
    adapters.register_dumper("numpy.uint64", NPNumericBinaryDumper)
    adapters.register_dumper("numpy.ulonglong", NPNumericBinaryDumper)
    adapters.register_dumper("numpy.float16", Float4BinaryDumper)
    adapters.register_dumper("numpy.float32", Float4BinaryDumper)
    adapters.register_dumper("numpy.float64", FloatBinaryDumper)
