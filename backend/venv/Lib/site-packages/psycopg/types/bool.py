"""
Adapters for booleans.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from .. import _oids
from ..pq import Format
from ..abc import AdaptContext
from ..adapt import Buffer, Dumper, Loader


class BoolDumper(Dumper):
    oid = _oids.BOOL_OID

    def dump(self, obj: bool) -> Buffer | None:
        return b"t" if obj else b"f"

    def quote(self, obj: bool) -> Buffer:
        return b"true" if obj else b"false"


class BoolBinaryDumper(Dumper):
    format = Format.BINARY
    oid = _oids.BOOL_OID

    def dump(self, obj: bool) -> Buffer | None:
        return b"\x01" if obj else b"\x00"


class BoolLoader(Loader):
    def load(self, data: Buffer) -> bool:
        return data == b"t"


class BoolBinaryLoader(Loader):
    format = Format.BINARY

    def load(self, data: Buffer) -> bool:
        return data != b"\x00"


def register_default_adapters(context: AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper(bool, BoolDumper)
    adapters.register_dumper(bool, BoolBinaryDumper)
    adapters.register_loader("bool", BoolLoader)
    adapters.register_loader("bool", BoolBinaryLoader)
