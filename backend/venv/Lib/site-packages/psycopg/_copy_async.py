"""
Objects to support the COPY protocol (async version).
"""

# Copyright (C) 2023 The Psycopg Team

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncIterator, Sequence

from . import errors as e
from . import pq
from ._compat import Self
from ._acompat import AQueue, AWorker, agather, aspawn
from ._copy_base import MAX_BUFFER_SIZE, PREFER_FLUSH, QUEUE_SIZE, BaseCopy
from .generators import copy_end, copy_to

if TYPE_CHECKING:
    from .abc import Buffer
    from .cursor_async import AsyncCursor
    from .connection_async import AsyncConnection  # noqa: F401

COPY_IN = pq.ExecStatus.COPY_IN
COPY_OUT = pq.ExecStatus.COPY_OUT

ACTIVE = pq.TransactionStatus.ACTIVE


class AsyncCopy(BaseCopy["AsyncConnection[Any]"]):
    """Manage an asynchronous :sql:`COPY` operation.

    :param cursor: the cursor where the operation is performed.
    :param binary: if `!True`, write binary format.
    :param writer: the object to write to destination. If not specified, write
        to the `!cursor` connection.

    Choosing `!binary` is not necessary if the cursor has executed a
    :sql:`COPY` operation, because the operation result describes the format
    too. The parameter is useful when a `!Copy` object is created manually and
    no operation is performed on the cursor, such as when using ``writer=``\\
    `~psycopg.copy.FileWriter`.
    """

    __module__ = "psycopg"

    writer: AsyncWriter

    def __init__(
        self,
        cursor: AsyncCursor[Any],
        *,
        binary: bool | None = None,
        writer: AsyncWriter | None = None,
    ):
        super().__init__(cursor, binary=binary)
        if not writer:
            writer = AsyncLibpqWriter(cursor)

        self.writer = writer
        self._write = writer.write

    async def __aenter__(self) -> Self:
        self._enter()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.finish(exc_val)

    # End user sync interface

    async def __aiter__(self) -> AsyncIterator[Buffer]:
        """Implement block-by-block iteration on :sql:`COPY TO`."""
        while True:
            data = await self.read()
            if not data:
                break
            yield data

    async def read(self) -> Buffer:
        """
        Read an unparsed row after a :sql:`COPY TO` operation.

        Return an empty string when the data is finished.
        """
        return await self.connection.wait(self._read_gen())

    async def rows(self) -> AsyncIterator[tuple[Any, ...]]:
        """
        Iterate on the result of a :sql:`COPY TO` operation record by record.

        Note that the records returned will be tuples of unparsed strings or
        bytes, unless data types are specified using `set_types()`.
        """
        while True:
            record = await self.read_row()
            if record is None:
                break
            yield record

    async def read_row(self) -> tuple[Any, ...] | None:
        """
        Read a parsed row of data from a table after a :sql:`COPY TO` operation.

        Return `!None` when the data is finished.

        Note that the records returned will be tuples of unparsed strings or
        bytes, unless data types are specified using `set_types()`.
        """
        return await self.connection.wait(self._read_row_gen())

    async def write(self, buffer: Buffer | str) -> None:
        """
        Write a block of data to a table after a :sql:`COPY FROM` operation.

        If the :sql:`COPY` is in binary format `!buffer` must be `!bytes`. In
        text mode it can be either `!bytes` or `!str`.
        """
        data = self.formatter.write(buffer)
        if data:
            await self._write(data)

    async def write_row(self, row: Sequence[Any]) -> None:
        """Write a record to a table after a :sql:`COPY FROM` operation."""
        data = self.formatter.write_row(row)
        if data:
            await self._write(data)

    async def finish(self, exc: BaseException | None) -> None:
        """Terminate the copy operation and free the resources allocated.

        You shouldn't need to call this function yourself: it is usually called
        by exit. It is available if, despite what is documented, you end up
        using the `Copy` object outside a block.
        """
        if self._direction == COPY_IN:
            data = self.formatter.end()
            if data:
                await self._write(data)
            await self.writer.finish(exc)
            self._finished = True
        else:
            if not exc:
                return

            if self._pgconn.transaction_status != ACTIVE:
                # The server has already finished to send copy data. The connection
                # is already in a good state.
                return

            # Throw a cancel to the server, then consume the rest of the copy data
            # (which might or might not have been already transferred entirely to
            # the client, so we won't necessary see the exception associated with
            # canceling).
            await self.connection._try_cancel()
            await self.connection.wait(self._end_copy_out_gen())


class AsyncWriter(ABC):
    """
    A class to write copy data somewhere (for async connections).
    """

    @abstractmethod
    async def write(self, data: Buffer) -> None:
        """Write some data to destination."""
        ...

    async def finish(self, exc: BaseException | None = None) -> None:
        """
        Called when write operations are finished.

        If operations finished with an error, it will be passed to ``exc``.
        """
        pass


class AsyncLibpqWriter(AsyncWriter):
    """
    An `AsyncWriter` to write copy data to a Postgres database.
    """

    __module__ = "psycopg.copy"

    def __init__(self, cursor: AsyncCursor[Any]):
        self.cursor = cursor
        self.connection = cursor.connection
        self._pgconn = self.connection.pgconn

    async def write(self, data: Buffer) -> None:
        if len(data) <= MAX_BUFFER_SIZE:
            # Most used path: we don't need to split the buffer in smaller
            # bits, so don't make a copy.
            await self.connection.wait(copy_to(self._pgconn, data, flush=PREFER_FLUSH))
        else:
            # Copy a buffer too large in chunks to avoid causing a memory
            # error in the libpq, which may cause an infinite loop (#255).
            for i in range(0, len(data), MAX_BUFFER_SIZE):
                await self.connection.wait(
                    copy_to(
                        self._pgconn, data[i : i + MAX_BUFFER_SIZE], flush=PREFER_FLUSH
                    )
                )

    async def finish(self, exc: BaseException | None = None) -> None:
        bmsg: bytes | None
        if exc:
            msg = f"error from Python: {type(exc).__qualname__} - {exc}"
            bmsg = msg.encode(self._pgconn._encoding, "replace")
        else:
            bmsg = None

        try:
            res = await self.connection.wait(copy_end(self._pgconn, bmsg))
        # The QueryCanceled is expected if we sent an exception message to
        # pgconn.put_copy_end(). The Python exception that generated that
        # cancelling is more important, so don't clobber it.
        except e.QueryCanceled:
            if not bmsg:
                raise
        else:
            self.cursor._results = [res]


class AsyncQueuedLibpqWriter(AsyncLibpqWriter):
    """
    `AsyncWriter` using a buffer to queue data to write.

    `write()` returns immediately, so that the main thread can be CPU-bound
    formatting messages, while a worker thread can be IO-bound waiting to write
    on the connection.
    """

    __module__ = "psycopg.copy"

    def __init__(self, cursor: AsyncCursor[Any]):
        super().__init__(cursor)

        self._queue: AQueue[Buffer] = AQueue(maxsize=QUEUE_SIZE)
        self._worker: AWorker | None = None
        self._worker_error: BaseException | None = None

    async def worker(self) -> None:
        """Push data to the server when available from the copy queue.

        Terminate reading when the queue receives a false-y value, or in case
        of error.

        The function is designed to be run in a separate task.
        """
        try:
            while True:
                data = await self._queue.get()
                if not data:
                    break
                await self.connection.wait(
                    copy_to(self._pgconn, data, flush=PREFER_FLUSH)
                )
        except BaseException as ex:
            # Propagate the error to the main thread.
            self._worker_error = ex

    async def write(self, data: Buffer) -> None:
        if not self._worker:
            # warning: reference loop, broken by _write_end
            self._worker = aspawn(self.worker)

        # If the worker thread raies an exception, re-raise it to the caller.
        if self._worker_error:
            raise self._worker_error

        if len(data) <= MAX_BUFFER_SIZE:
            # Most used path: we don't need to split the buffer in smaller
            # bits, so don't make a copy.
            await self._queue.put(data)
        else:
            # Copy a buffer too large in chunks to avoid causing a memory
            # error in the libpq, which may cause an infinite loop (#255).
            for i in range(0, len(data), MAX_BUFFER_SIZE):
                await self._queue.put(data[i : i + MAX_BUFFER_SIZE])

    async def finish(self, exc: BaseException | None = None) -> None:
        await self._queue.put(b"")

        if self._worker:
            await agather(self._worker)
            self._worker = None  # break reference loops if any

        # Check if the worker thread raised any exception before terminating.
        if self._worker_error:
            raise self._worker_error

        await super().finish(exc)
