"""
Compatibility objects with DBAPI 2.0
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import time
import datetime as dt
from math import floor
from typing import Any, Sequence

from . import _oids
from .abc import AdaptContext, Buffer
from .types.string import BytesBinaryDumper, BytesDumper


class DBAPITypeObject:
    def __init__(self, name: str, oids: Sequence[int]):
        self.name = name
        self.values = tuple(oids)

    def __repr__(self) -> str:
        return f"psycopg.{self.name}"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, int):
            return other in self.values
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, int):
            return other not in self.values
        else:
            return NotImplemented


BINARY = DBAPITypeObject("BINARY", (_oids.BYTEA_OID,))
DATETIME = DBAPITypeObject(
    "DATETIME",
    (
        _oids.TIMESTAMP_OID,
        _oids.TIMESTAMPTZ_OID,
        _oids.DATE_OID,
        _oids.TIME_OID,
        _oids.TIMETZ_OID,
        _oids.INTERVAL_OID,
    ),
)
NUMBER = DBAPITypeObject(
    "NUMBER",
    (
        _oids.INT2_OID,
        _oids.INT4_OID,
        _oids.INT8_OID,
        _oids.FLOAT4_OID,
        _oids.FLOAT8_OID,
        _oids.NUMERIC_OID,
    ),
)
ROWID = DBAPITypeObject("ROWID", (_oids.OID_OID,))
STRING = DBAPITypeObject(
    "STRING", (_oids.TEXT_OID, _oids.VARCHAR_OID, _oids.BPCHAR_OID)
)


class Binary:
    def __init__(self, obj: Any):
        self.obj = obj

    def __repr__(self) -> str:
        sobj = repr(self.obj)
        if len(sobj) > 40:
            sobj = f"{sobj[:35]} ... ({len(sobj)} byteschars)"
        return f"{self.__class__.__name__}({sobj})"


class BinaryBinaryDumper(BytesBinaryDumper):
    def dump(self, obj: Buffer | Binary) -> Buffer | None:
        if isinstance(obj, Binary):
            return super().dump(obj.obj)
        else:
            return super().dump(obj)


class BinaryTextDumper(BytesDumper):
    def dump(self, obj: Buffer | Binary) -> Buffer | None:
        if isinstance(obj, Binary):
            return super().dump(obj.obj)
        else:
            return super().dump(obj)


def Date(year: int, month: int, day: int) -> dt.date:
    return dt.date(year, month, day)


def DateFromTicks(ticks: float) -> dt.date:
    return TimestampFromTicks(ticks).date()


def Time(hour: int, minute: int, second: int) -> dt.time:
    return dt.time(hour, minute, second)


def TimeFromTicks(ticks: float) -> dt.time:
    return TimestampFromTicks(ticks).time()


def Timestamp(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> dt.datetime:
    return dt.datetime(year, month, day, hour, minute, second)


def TimestampFromTicks(ticks: float) -> dt.datetime:
    secs = floor(ticks)
    frac = ticks - secs
    t = time.localtime(ticks)
    tzinfo = dt.timezone(dt.timedelta(seconds=t.tm_gmtoff))
    rv = dt.datetime(*t[:6], round(frac * 1_000_000), tzinfo=tzinfo)
    return rv


def register_dbapi20_adapters(context: AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper(Binary, BinaryTextDumper)
    adapters.register_dumper(Binary, BinaryBinaryDumper)

    # Make them also the default dumpers when dumping by bytea oid
    adapters.register_dumper(None, BinaryTextDumper)
    adapters.register_dumper(None, BinaryBinaryDumper)
