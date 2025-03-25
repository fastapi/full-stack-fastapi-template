"""
Psycopg AsyncCursor object.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterable, overload
from contextlib import asynccontextmanager

from . import errors as e
from . import pq
from .abc import Params, Query
from .copy import AsyncCopy, AsyncWriter
from .rows import AsyncRowFactory, Row, RowMaker
from ._compat import Self
from ._pipeline import Pipeline
from ._cursor_base import BaseCursor

if TYPE_CHECKING:
    from .connection_async import AsyncConnection

ACTIVE = pq.TransactionStatus.ACTIVE


class AsyncCursor(BaseCursor["AsyncConnection[Any]", Row]):
    __module__ = "psycopg"
    __slots__ = ()

    @overload
    def __init__(self, connection: AsyncConnection[Row]): ...

    @overload
    def __init__(
        self, connection: AsyncConnection[Any], *, row_factory: AsyncRowFactory[Row]
    ): ...

    def __init__(
        self,
        connection: AsyncConnection[Any],
        *,
        row_factory: AsyncRowFactory[Row] | None = None,
    ):
        super().__init__(connection)
        self._row_factory = row_factory or connection.row_factory

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Close the current cursor and free associated resources.
        """
        self._close()

    @property
    def row_factory(self) -> AsyncRowFactory[Row]:
        """Writable attribute to control how result rows are formed."""
        return self._row_factory

    @row_factory.setter
    def row_factory(self, row_factory: AsyncRowFactory[Row]) -> None:
        self._row_factory = row_factory
        if self.pgresult:
            self._make_row = row_factory(self)

    def _make_row_maker(self) -> RowMaker[Row]:
        return self._row_factory(self)

    async def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
    ) -> Self:
        """
        Execute a query or command to the database.
        """
        try:
            async with self._conn.lock:
                await self._conn.wait(
                    self._execute_gen(query, params, prepare=prepare, binary=binary)
                )
        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)
        return self

    async def executemany(
        self,
        query: Query,
        params_seq: Iterable[Params],
        *,
        returning: bool = False,
    ) -> None:
        """
        Execute the same command with a sequence of input data.
        """
        try:
            if Pipeline.is_supported():
                # If there is already a pipeline, ride it, in order to avoid
                # sending unnecessary Sync.
                async with self._conn.lock:
                    p = self._conn._pipeline
                    if p:
                        await self._conn.wait(
                            self._executemany_gen_pipeline(query, params_seq, returning)
                        )
                # Otherwise, make a new one
                if not p:
                    async with self._conn.pipeline(), self._conn.lock:
                        await self._conn.wait(
                            self._executemany_gen_pipeline(query, params_seq, returning)
                        )
            else:
                async with self._conn.lock:
                    await self._conn.wait(
                        self._executemany_gen_no_pipeline(query, params_seq, returning)
                    )
        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)

    async def stream(
        self,
        query: Query,
        params: Params | None = None,
        *,
        binary: bool | None = None,
        size: int = 1,
    ) -> AsyncIterator[Row]:
        """
        Iterate row-by-row on a result from the database.

        :param size: if greater than 1, results will be retrieved by chunks of
            this size from the server (but still yielded row-by-row); this is only
            available from version 17 of the libpq.
        """
        if self._pgconn.pipeline_status:
            raise e.ProgrammingError("stream() cannot be used in pipeline mode")

        async with self._conn.lock:
            try:
                await self._conn.wait(
                    self._stream_send_gen(query, params, binary=binary, size=size)
                )
                first = True
                while await self._conn.wait(self._stream_fetchone_gen(first)):
                    for pos in range(size):
                        rec = self._tx.load_row(pos, self._make_row)
                        if rec is None:
                            break
                        yield rec
                    first = False

            except e._NO_TRACEBACK as ex:
                raise ex.with_traceback(None)

            finally:
                if self._pgconn.transaction_status == ACTIVE:
                    # Try to cancel the query, then consume the results
                    # already received.
                    await self._conn._try_cancel()
                    try:
                        while await self._conn.wait(
                            self._stream_fetchone_gen(first=False)
                        ):
                            pass
                    except Exception:
                        pass

                    # Try to get out of ACTIVE state. Just do a single attempt, which
                    # should work to recover from an error or query cancelled.
                    try:
                        await self._conn.wait(self._stream_fetchone_gen(first=False))
                    except Exception:
                        pass

    async def fetchone(self) -> Row | None:
        """
        Return the next record from the current recordset.

        Return `!None` the recordset is finished.

        :rtype: Row | None, with Row defined by `row_factory`
        """
        await self._fetch_pipeline()
        self._check_result_for_fetch()
        record = self._tx.load_row(self._pos, self._make_row)
        if record is not None:
            self._pos += 1
        return record

    async def fetchmany(self, size: int = 0) -> list[Row]:
        """
        Return the next `!size` records from the current recordset.

        `!size` default to `!self.arraysize` if not specified.

        :rtype: Sequence[Row], with Row defined by `row_factory`
        """
        await self._fetch_pipeline()
        self._check_result_for_fetch()
        assert self.pgresult

        if not size:
            size = self.arraysize
        records = self._tx.load_rows(
            self._pos,
            min(self._pos + size, self.pgresult.ntuples),
            self._make_row,
        )
        self._pos += len(records)
        return records

    async def fetchall(self) -> list[Row]:
        """
        Return all the remaining records from the current recordset.

        :rtype: Sequence[Row], with Row defined by `row_factory`
        """
        await self._fetch_pipeline()
        self._check_result_for_fetch()
        assert self.pgresult
        records = self._tx.load_rows(self._pos, self.pgresult.ntuples, self._make_row)
        self._pos = self.pgresult.ntuples
        return records

    async def __aiter__(self) -> AsyncIterator[Row]:
        await self._fetch_pipeline()
        self._check_result_for_fetch()

        def load(pos: int) -> Row | None:
            return self._tx.load_row(pos, self._make_row)

        while True:
            row = load(self._pos)
            if row is None:
                break
            self._pos += 1
            yield row

    async def scroll(self, value: int, mode: str = "relative") -> None:
        """
        Move the cursor in the result set to a new position according to mode.

        If `!mode` is ``'relative'`` (default), `!value` is taken as offset to
        the current position in the result set; if set to ``'absolute'``,
        `!value` states an absolute target position.

        Raise `!IndexError` in case a scroll operation would leave the result
        set. In this case the position will not change.
        """
        await self._fetch_pipeline()
        self._scroll(value, mode)

    @asynccontextmanager
    async def copy(
        self,
        statement: Query,
        params: Params | None = None,
        *,
        writer: AsyncWriter | None = None,
    ) -> AsyncIterator[AsyncCopy]:
        """
        Initiate a :sql:`COPY` operation and return an object to manage it.
        """
        try:
            async with self._conn.lock:
                await self._conn.wait(self._start_copy_gen(statement, params))

            async with AsyncCopy(self, writer=writer) as copy:
                yield copy
        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)

        # If a fresher result has been set on the cursor by the Copy object,
        # read its properties (especially rowcount).
        self._select_current_result(0)

    async def _fetch_pipeline(self) -> None:
        if (
            self._execmany_returning is not False
            and not self.pgresult
            and self._conn._pipeline
        ):
            async with self._conn.lock:
                await self._conn.wait(self._conn._pipeline._fetch_gen(flush=True))
