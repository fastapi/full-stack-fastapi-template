"""
psycopg copy support
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import re
import sys
import struct
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Match, Sequence

from . import adapt
from . import errors as e
from . import pq
from .abc import Buffer, ConnectionType, PQGen, Transformer
from .pq.misc import connection_summary
from ._cmodule import _psycopg
from .generators import copy_from

if TYPE_CHECKING:
    from ._cursor_base import BaseCursor

PY_TEXT = adapt.PyFormat.TEXT
PY_BINARY = adapt.PyFormat.BINARY

TEXT = pq.Format.TEXT
BINARY = pq.Format.BINARY

COPY_IN = pq.ExecStatus.COPY_IN
COPY_OUT = pq.ExecStatus.COPY_OUT

# Size of data to accumulate before sending it down the network. We fill a
# buffer this size field by field, and when it passes the threshold size
# we ship it, so it may end up being bigger than this.
BUFFER_SIZE = 32 * 1024

# Maximum data size we want to queue to send to the libpq copy. Sending a
# buffer too big to be handled can cause an infinite loop in the libpq
# (#255) so we want to split it in more digestable chunks.
MAX_BUFFER_SIZE = 4 * BUFFER_SIZE
# Note: making this buffer too large, e.g.
# MAX_BUFFER_SIZE = 1024 * 1024
# makes operations *way* slower! Probably triggering some quadraticity
# in the libpq memory management and data sending.

# Max size of the write queue of buffers. More than that copy will block
# Each buffer should be around BUFFER_SIZE size.
QUEUE_SIZE = 1024

# On certain systems, memmove seems particularly slow and flushing often is
# more performing than accumulating a larger buffer. See #746 for details.
PREFER_FLUSH = sys.platform == "darwin"


class BaseCopy(Generic[ConnectionType]):
    """
    Base implementation for the copy user interface.

    Two subclasses expose real methods with the sync/async differences.

    The difference between the text and binary format is managed by two
    different `Formatter` subclasses.

    Writing (the I/O part) is implemented in the subclasses by a `Writer` or
    `AsyncWriter` instance. Normally writing implies sending copy data to a
    database, but a different writer might be chosen, e.g. to stream data into
    a file for later use.
    """

    formatter: Formatter

    def __init__(
        self,
        cursor: BaseCursor[ConnectionType, Any],
        *,
        binary: bool | None = None,
    ):
        self.cursor = cursor
        self.connection = cursor.connection
        self._pgconn = self.connection.pgconn

        result = cursor.pgresult
        if result:
            self._direction = result.status
            if self._direction != COPY_IN and self._direction != COPY_OUT:
                raise e.ProgrammingError(
                    "the cursor should have performed a COPY operation;"
                    f" its status is {pq.ExecStatus(self._direction).name} instead"
                )
        else:
            self._direction = COPY_IN

        if binary is None:
            binary = bool(result and result.binary_tuples)

        tx: Transformer = getattr(cursor, "_tx", None) or adapt.Transformer(cursor)
        if binary:
            self.formatter = BinaryFormatter(tx)
        else:
            self.formatter = TextFormatter(tx, encoding=self._pgconn._encoding)

        self._finished = False

    def __repr__(self) -> str:
        cls = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        info = connection_summary(self._pgconn)
        return f"<{cls} {info} at 0x{id(self):x}>"

    def _enter(self) -> None:
        if self._finished:
            raise TypeError("copy blocks can be used only once")

    def set_types(self, types: Sequence[int | str]) -> None:
        """
        Set the types expected in a COPY operation.

        The types must be specified as a sequence of oid or PostgreSQL type
        names (e.g. ``int4``, ``timestamptz[]``).

        This operation overcomes the lack of metadata returned by PostgreSQL
        when a COPY operation begins:

        - On :sql:`COPY TO`, `!set_types()` allows to specify what types the
          operation returns. If `!set_types()` is not used, the data will be
          returned as unparsed strings or bytes instead of Python objects.

        - On :sql:`COPY FROM`, `!set_types()` allows to choose what type the
          database expects. This is especially useful in binary copy, because
          PostgreSQL will apply no cast rule.

        """
        registry = self.cursor.adapters.types
        oids = [t if isinstance(t, int) else registry.get_oid(t) for t in types]

        if self._direction == COPY_IN:
            self.formatter.transformer.set_dumper_types(oids, self.formatter.format)
        else:
            self.formatter.transformer.set_loader_types(oids, self.formatter.format)

    # High level copy protocol generators (state change of the Copy object)

    def _read_gen(self) -> PQGen[Buffer]:
        if self._finished:
            return memoryview(b"")

        res = yield from copy_from(self._pgconn)
        if isinstance(res, memoryview):
            return res

        # res is the final PGresult
        self._finished = True

        # This result is a COMMAND_OK which has info about the number of rows
        # returned, but not about the columns, which is instead an information
        # that was received on the COPY_OUT result at the beginning of COPY.
        # So, don't replace the results in the cursor, just update the rowcount.
        nrows = res.command_tuples
        self.cursor._rowcount = nrows if nrows is not None else -1
        return memoryview(b"")

    def _read_row_gen(self) -> PQGen[tuple[Any, ...] | None]:
        data = yield from self._read_gen()
        if not data:
            return None

        row = self.formatter.parse_row(data)
        if row is None:
            # Get the final result to finish the copy operation
            yield from self._read_gen()
            self._finished = True
            return None

        return row

    def _end_copy_out_gen(self) -> PQGen[None]:
        try:
            while (yield from self._read_gen()):
                pass
        except e.QueryCanceled:
            pass


class Formatter(ABC):
    """
    A class which understand a copy format (text, binary).
    """

    format: pq.Format

    def __init__(self, transformer: Transformer):
        self.transformer = transformer
        self._write_buffer = bytearray()
        self._row_mode = False  # true if the user is using write_row()

    @abstractmethod
    def parse_row(self, data: Buffer) -> tuple[Any, ...] | None: ...

    @abstractmethod
    def write(self, buffer: Buffer | str) -> Buffer: ...

    @abstractmethod
    def write_row(self, row: Sequence[Any]) -> Buffer: ...

    @abstractmethod
    def end(self) -> Buffer: ...


class TextFormatter(Formatter):
    format = TEXT

    def __init__(self, transformer: Transformer, encoding: str = "utf-8"):
        super().__init__(transformer)
        self._encoding = encoding

    def parse_row(self, data: Buffer) -> tuple[Any, ...] | None:
        rv: tuple[Any, ...] | None = None
        if data:
            rv = parse_row_text(data, self.transformer)

        return rv

    def write(self, buffer: Buffer | str) -> Buffer:
        data = self._ensure_bytes(buffer)
        self._signature_sent = True
        return data

    def write_row(self, row: Sequence[Any]) -> Buffer:
        # Note down that we are writing in row mode: it means we will have
        # to take care of the end-of-copy marker too
        self._row_mode = True

        format_row_text(row, self.transformer, self._write_buffer)
        if len(self._write_buffer) > BUFFER_SIZE:
            buffer, self._write_buffer = self._write_buffer, bytearray()
            return buffer
        else:
            return b""

    def end(self) -> Buffer:
        buffer, self._write_buffer = self._write_buffer, bytearray()
        return buffer

    def _ensure_bytes(self, data: Buffer | str) -> Buffer:
        if isinstance(data, str):
            return data.encode(self._encoding)
        else:
            # Assume, for simplicity, that the user is not passing stupid
            # things to the write function. If that's the case, things
            # will fail downstream.
            return data


class BinaryFormatter(Formatter):
    format = BINARY

    def __init__(self, transformer: Transformer):
        super().__init__(transformer)
        self._signature_sent = False

    def parse_row(self, data: Buffer) -> tuple[Any, ...] | None:
        rv: tuple[Any, ...] | None = None

        if not self._signature_sent:
            if data[: len(_binary_signature)] != _binary_signature:
                raise e.DataError(
                    "binary copy doesn't start with the expected signature"
                )
            self._signature_sent = True
            data = data[len(_binary_signature) :]

        if data != _binary_trailer:
            rv = parse_row_binary(data, self.transformer)

        return rv

    def write(self, buffer: Buffer | str) -> Buffer:
        data = self._ensure_bytes(buffer)
        self._signature_sent = True
        return data

    def write_row(self, row: Sequence[Any]) -> Buffer:
        # Note down that we are writing in row mode: it means we will have
        # to take care of the end-of-copy marker too
        self._row_mode = True

        if not self._signature_sent:
            self._write_buffer += _binary_signature
            self._signature_sent = True

        format_row_binary(row, self.transformer, self._write_buffer)
        if len(self._write_buffer) > BUFFER_SIZE:
            buffer, self._write_buffer = self._write_buffer, bytearray()
            return buffer
        else:
            return b""

    def end(self) -> Buffer:
        # If we have sent no data we need to send the signature
        # and the trailer
        if not self._signature_sent:
            self._write_buffer += _binary_signature
            self._write_buffer += _binary_trailer

        elif self._row_mode:
            # if we have sent data already, we have sent the signature
            # too (either with the first row, or we assume that in
            # block mode the signature is included).
            # Write the trailer only if we are sending rows (with the
            # assumption that who is copying binary data is sending the
            # whole format).
            self._write_buffer += _binary_trailer

        buffer, self._write_buffer = self._write_buffer, bytearray()
        return buffer

    def _ensure_bytes(self, data: Buffer | str) -> Buffer:
        if isinstance(data, str):
            raise TypeError("cannot copy str data in binary mode: use bytes instead")
        else:
            # Assume, for simplicity, that the user is not passing stupid
            # things to the write function. If that's the case, things
            # will fail downstream.
            return data


def _format_row_text(
    row: Sequence[Any], tx: Transformer, out: bytearray | None = None
) -> bytearray:
    """Convert a row of objects to the data to send for copy."""
    if out is None:
        out = bytearray()

    if not row:
        out += b"\n"
        return out

    adapted = tx.dump_sequence(row, [PY_TEXT] * len(row))
    for b in adapted:
        out += _dump_re.sub(_dump_sub, b) if b is not None else rb"\N"
        out += b"\t"

    out[-1:] = b"\n"
    return out


def _format_row_binary(
    row: Sequence[Any], tx: Transformer, out: bytearray | None = None
) -> bytearray:
    """Convert a row of objects to the data to send for binary copy."""
    if out is None:
        out = bytearray()

    out += _pack_int2(len(row))
    adapted = tx.dump_sequence(row, [PY_BINARY] * len(row))
    for b in adapted:
        if b is not None:
            out += _pack_int4(len(b))
            out += b
        else:
            out += _binary_null

    return out


def _parse_row_text(data: Buffer, tx: Transformer) -> tuple[Any, ...]:
    if not isinstance(data, bytes):
        data = bytes(data)
    fields = data.split(b"\t")
    fields[-1] = fields[-1][:-1]  # drop \n
    row = [None if f == b"\\N" else _load_re.sub(_load_sub, f) for f in fields]
    return tx.load_sequence(row)


def _parse_row_binary(data: Buffer, tx: Transformer) -> tuple[Any, ...]:
    row: list[Buffer | None] = []
    nfields = _unpack_int2(data, 0)[0]
    pos = 2
    for i in range(nfields):
        length = _unpack_int4(data, pos)[0]
        pos += 4
        if length >= 0:
            row.append(data[pos : pos + length])
            pos += length
        else:
            row.append(None)

    return tx.load_sequence(row)


_pack_int2 = struct.Struct("!h").pack
_pack_int4 = struct.Struct("!i").pack
_unpack_int2 = struct.Struct("!h").unpack_from
_unpack_int4 = struct.Struct("!i").unpack_from

_binary_signature = (
    b"PGCOPY\n\xff\r\n\0"  # Signature
    b"\x00\x00\x00\x00"  # flags
    b"\x00\x00\x00\x00"  # extra length
)
_binary_trailer = b"\xff\xff"
_binary_null = b"\xff\xff\xff\xff"

_dump_re = re.compile(b"[\b\t\n\v\f\r\\\\]")
_dump_repl = {
    b"\b": b"\\b",
    b"\t": b"\\t",
    b"\n": b"\\n",
    b"\v": b"\\v",
    b"\f": b"\\f",
    b"\r": b"\\r",
    b"\\": b"\\\\",
}


def _dump_sub(m: Match[bytes], __map: dict[bytes, bytes] = _dump_repl) -> bytes:
    return __map[m.group(0)]


_load_re = re.compile(b"\\\\[btnvfr\\\\]")
_load_repl = {v: k for k, v in _dump_repl.items()}


def _load_sub(m: Match[bytes], __map: dict[bytes, bytes] = _load_repl) -> bytes:
    return __map[m.group(0)]


# Override functions with fast versions if available
if _psycopg:
    format_row_text = _psycopg.format_row_text
    format_row_binary = _psycopg.format_row_binary
    parse_row_text = _psycopg.parse_row_text
    parse_row_binary = _psycopg.parse_row_binary

else:
    format_row_text = _format_row_text
    format_row_binary = _format_row_binary
    parse_row_text = _parse_row_text
    parse_row_binary = _parse_row_binary
