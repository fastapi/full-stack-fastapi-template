"""
Adapters for the UUID type.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .. import _oids
from ..pq import Format
from ..abc import AdaptContext
from ..adapt import Buffer, Dumper, Loader

if TYPE_CHECKING:
    import uuid

# Importing the uuid module is slow, so import it only on request.
UUID: Callable[..., uuid.UUID] = None  # type: ignore[assignment]


class UUIDDumper(Dumper):
    oid = _oids.UUID_OID

    def dump(self, obj: uuid.UUID) -> Buffer | None:
        return obj.hex.encode()


class UUIDBinaryDumper(UUIDDumper):
    format = Format.BINARY

    def dump(self, obj: uuid.UUID) -> Buffer | None:
        return obj.bytes


class UUIDLoader(Loader):
    def __init__(self, oid: int, context: AdaptContext | None = None):
        super().__init__(oid, context)
        global UUID
        if UUID is None:
            from uuid import UUID

    def load(self, data: Buffer) -> uuid.UUID:
        if isinstance(data, memoryview):
            data = bytes(data)
        return UUID(data.decode())


class UUIDBinaryLoader(UUIDLoader):
    format = Format.BINARY

    def load(self, data: Buffer) -> uuid.UUID:
        if isinstance(data, memoryview):
            data = bytes(data)
        return UUID(bytes=data)


def register_default_adapters(context: AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper("uuid.UUID", UUIDDumper)
    adapters.register_dumper("uuid.UUID", UUIDBinaryDumper)
    adapters.register_loader("uuid", UUIDLoader)
    adapters.register_loader("uuid", UUIDBinaryLoader)
