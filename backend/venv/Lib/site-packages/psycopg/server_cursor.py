"""
psycopg server-side cursor objects.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator, Iterable, Iterator, overload
from warnings import warn

from . import errors as e
from . import pq, sql
from .abc import ConnectionType, Params, PQGen, Query
from .rows import AsyncRowFactory, Row, RowFactory
from .cursor import Cursor
from ._compat import Self
from .generators import execute
from ._cursor_base import BaseCursor
from .cursor_async import AsyncCursor

if TYPE_CHECKING:
    from .connection import Connection
    from .connection_async import AsyncConnection

DEFAULT_ITERSIZE = 100

TEXT = pq.Format.TEXT
BINARY = pq.Format.BINARY

COMMAND_OK = pq.ExecStatus.COMMAND_OK
TUPLES_OK = pq.ExecStatus.TUPLES_OK

IDLE = pq.TransactionStatus.IDLE
INTRANS = pq.TransactionStatus.INTRANS


class ServerCursorMixin(BaseCursor[ConnectionType, Row]):
    """Mixin to add ServerCursor behaviour and implementation a BaseCursor."""

    __slots__ = "_name _scrollable _withhold _described itersize _format".split()

    def __init__(
        self,
        name: str,
        scrollable: bool | None,
        withhold: bool,
    ):
        self._name = name
        self._scrollable = scrollable
        self._withhold = withhold
        self._described = False
        self.itersize: int = DEFAULT_ITERSIZE
        self._format = TEXT

    def __repr__(self) -> str:
        # Insert the name as the second word
        parts = super().__repr__().split(None, 1)
        parts.insert(1, f"{self._name!r}")
        return " ".join(parts)

    @property
    def name(self) -> str:
        """The name of the cursor."""
        return self._name

    @property
    def scrollable(self) -> bool | None:
        """
        Whether the cursor is scrollable or not.

        If `!None` leave the choice to the server. Use `!True` if you want to
        use `scroll()` on the cursor.
        """
        return self._scrollable

    @property
    def withhold(self) -> bool:
        """
        If the cursor can be used after the creating transaction has committed.
        """
        return self._withhold

    @property
    def rownumber(self) -> int | None:
        """Index of the next row to fetch in the current result.

        `!None` if there is no result to fetch.
        """
        res = self.pgresult
        # command_status is empty if the result comes from
        # describe_portal, which means that we have just executed the DECLARE,
        # so we can assume we are at the first row.
        tuples = res and (res.status == TUPLES_OK or res.command_status == b"")
        return self._pos if tuples else None

    def _declare_gen(
        self,
        query: Query,
        params: Params | None = None,
        binary: bool | None = None,
    ) -> PQGen[None]:
        """Generator implementing `ServerCursor.execute()`."""

        query = self._make_declare_statement(query)

        # If the cursor is being reused, the previous one must be closed.
        if self._described:
            yield from self._close_gen()
            self._described = False

        yield from self._start_query(query)
        pgq = self._convert_query(query, params)
        self._execute_send(pgq, force_extended=True)
        results = yield from execute(self._conn.pgconn)
        if results[-1].status != COMMAND_OK:
            self._raise_for_result(results[-1])

        # Set the format, which will be used by describe and fetch operations
        if binary is None:
            self._format = self.format
        else:
            self._format = BINARY if binary else TEXT

        # The above result only returned COMMAND_OK. Get the cursor shape
        yield from self._describe_gen()

    def _describe_gen(self) -> PQGen[None]:
        self._pgconn.send_describe_portal(self._name.encode(self._encoding))
        results = yield from execute(self._pgconn)
        self._check_results(results)
        self._results = results
        self._select_current_result(0, format=self._format)
        self._described = True

    def _close_gen(self) -> PQGen[None]:
        ts = self._conn.pgconn.transaction_status

        # if the connection is not in a sane state, don't even try
        if ts != IDLE and ts != INTRANS:
            return

        # If we are IDLE, a WITHOUT HOLD cursor will surely have gone already.
        if not self._withhold and ts == IDLE:
            return

        # if we didn't declare the cursor ourselves we still have to close it
        # but we must make sure it exists.
        if not self._described:
            query = sql.SQL(
                "SELECT 1 FROM pg_catalog.pg_cursors WHERE name = {}"
            ).format(sql.Literal(self._name))
            res = yield from self._conn._exec_command(query)
            # pipeline mode otherwise, unsupported here.
            assert res is not None
            if res.ntuples == 0:
                return

        query = sql.SQL("CLOSE {}").format(sql.Identifier(self._name))
        yield from self._conn._exec_command(query)

    def _fetch_gen(self, num: int | None) -> PQGen[list[Row]]:
        if self.closed:
            raise e.InterfaceError("the cursor is closed")
        # If we are stealing the cursor, make sure we know its shape
        if not self._described:
            yield from self._start_query()
            yield from self._describe_gen()

        query = sql.SQL("FETCH FORWARD {} FROM {}").format(
            sql.SQL("ALL") if num is None else sql.Literal(num),
            sql.Identifier(self._name),
        )
        res = yield from self._conn._exec_command(query, result_format=self._format)
        # pipeline mode otherwise, unsupported here.
        assert res is not None

        self.pgresult = res
        self._tx.set_pgresult(res, set_loaders=False)
        return self._tx.load_rows(0, res.ntuples, self._make_row)

    def _scroll_gen(self, value: int, mode: str) -> PQGen[None]:
        if mode not in ("relative", "absolute"):
            raise ValueError(f"bad mode: {mode}. It should be 'relative' or 'absolute'")
        query = sql.SQL("MOVE{} {} FROM {}").format(
            sql.SQL(" ABSOLUTE" if mode == "absolute" else ""),
            sql.Literal(value),
            sql.Identifier(self._name),
        )
        yield from self._conn._exec_command(query)

    def _make_declare_statement(self, query: Query) -> sql.Composed:
        if isinstance(query, bytes):
            query = query.decode(self._encoding)
        if not isinstance(query, sql.Composable):
            query = sql.SQL(query)

        parts = [
            sql.SQL("DECLARE"),
            sql.Identifier(self._name),
        ]
        if self._scrollable is not None:
            parts.append(sql.SQL("SCROLL" if self._scrollable else "NO SCROLL"))
        parts.append(sql.SQL("CURSOR"))
        if self._withhold:
            parts.append(sql.SQL("WITH HOLD"))
        parts.append(sql.SQL("FOR"))
        parts.append(query)

        return sql.SQL(" ").join(parts)


class ServerCursor(ServerCursorMixin["Connection[Any]", Row], Cursor[Row]):
    __module__ = "psycopg"
    __slots__ = ()

    @overload
    def __init__(
        self,
        connection: Connection[Row],
        name: str,
        *,
        scrollable: bool | None = None,
        withhold: bool = False,
    ): ...

    @overload
    def __init__(
        self,
        connection: Connection[Any],
        name: str,
        *,
        row_factory: RowFactory[Row],
        scrollable: bool | None = None,
        withhold: bool = False,
    ): ...

    def __init__(
        self,
        connection: Connection[Any],
        name: str,
        *,
        row_factory: RowFactory[Row] | None = None,
        scrollable: bool | None = None,
        withhold: bool = False,
    ):
        Cursor.__init__(
            self, connection, row_factory=row_factory or connection.row_factory
        )
        ServerCursorMixin.__init__(self, name, scrollable, withhold)

    def __del__(self) -> None:
        if not self.closed:
            warn(
                f"the server-side cursor {self} was deleted while still open."
                " Please use 'with' or '.close()' to close the cursor properly",
                ResourceWarning,
            )

    def close(self) -> None:
        """
        Close the current cursor and free associated resources.
        """
        with self._conn.lock:
            if self.closed:
                return
            if not self._conn.closed:
                self._conn.wait(self._close_gen())
            super().close()

    def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        binary: bool | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Open a cursor to execute a query to the database.
        """
        if kwargs:
            raise TypeError(f"keyword not supported: {list(kwargs)[0]}")
        if self._pgconn.pipeline_status:
            raise e.NotSupportedError(
                "server-side cursors not supported in pipeline mode"
            )

        try:
            with self._conn.lock:
                self._conn.wait(self._declare_gen(query, params, binary))
        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)

        return self

    def executemany(
        self,
        query: Query,
        params_seq: Iterable[Params],
        *,
        returning: bool = True,
    ) -> None:
        """Method not implemented for server-side cursors."""
        raise e.NotSupportedError("executemany not supported on server-side cursors")

    def fetchone(self) -> Row | None:
        with self._conn.lock:
            recs = self._conn.wait(self._fetch_gen(1))
        if recs:
            self._pos += 1
            return recs[0]
        else:
            return None

    def fetchmany(self, size: int = 0) -> list[Row]:
        if not size:
            size = self.arraysize
        with self._conn.lock:
            recs = self._conn.wait(self._fetch_gen(size))
        self._pos += len(recs)
        return recs

    def fetchall(self) -> list[Row]:
        with self._conn.lock:
            recs = self._conn.wait(self._fetch_gen(None))
        self._pos += len(recs)
        return recs

    def __iter__(self) -> Iterator[Row]:
        while True:
            with self._conn.lock:
                recs = self._conn.wait(self._fetch_gen(self.itersize))
            for rec in recs:
                self._pos += 1
                yield rec
            if len(recs) < self.itersize:
                break

    def scroll(self, value: int, mode: str = "relative") -> None:
        with self._conn.lock:
            self._conn.wait(self._scroll_gen(value, mode))
        # Postgres doesn't have a reliable way to report a cursor out of bound
        if mode == "relative":
            self._pos += value
        else:
            self._pos = value


class AsyncServerCursor(
    ServerCursorMixin["AsyncConnection[Any]", Row], AsyncCursor[Row]
):
    __module__ = "psycopg"
    __slots__ = ()

    @overload
    def __init__(
        self,
        connection: AsyncConnection[Row],
        name: str,
        *,
        scrollable: bool | None = None,
        withhold: bool = False,
    ): ...

    @overload
    def __init__(
        self,
        connection: AsyncConnection[Any],
        name: str,
        *,
        row_factory: AsyncRowFactory[Row],
        scrollable: bool | None = None,
        withhold: bool = False,
    ): ...

    def __init__(
        self,
        connection: AsyncConnection[Any],
        name: str,
        *,
        row_factory: AsyncRowFactory[Row] | None = None,
        scrollable: bool | None = None,
        withhold: bool = False,
    ):
        AsyncCursor.__init__(
            self, connection, row_factory=row_factory or connection.row_factory
        )
        ServerCursorMixin.__init__(self, name, scrollable, withhold)

    def __del__(self) -> None:
        if not self.closed:
            warn(
                f"the server-side cursor {self} was deleted while still open."
                " Please use 'with' or '.close()' to close the cursor properly",
                ResourceWarning,
            )

    async def close(self) -> None:
        async with self._conn.lock:
            if self.closed:
                return
            if not self._conn.closed:
                await self._conn.wait(self._close_gen())
            await super().close()

    async def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        binary: bool | None = None,
        **kwargs: Any,
    ) -> Self:
        if kwargs:
            raise TypeError(f"keyword not supported: {list(kwargs)[0]}")
        if self._pgconn.pipeline_status:
            raise e.NotSupportedError(
                "server-side cursors not supported in pipeline mode"
            )

        try:
            async with self._conn.lock:
                await self._conn.wait(self._declare_gen(query, params, binary))
        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)

        return self

    async def executemany(
        self,
        query: Query,
        params_seq: Iterable[Params],
        *,
        returning: bool = True,
    ) -> None:
        raise e.NotSupportedError("executemany not supported on server-side cursors")

    async def fetchone(self) -> Row | None:
        async with self._conn.lock:
            recs = await self._conn.wait(self._fetch_gen(1))
        if recs:
            self._pos += 1
            return recs[0]
        else:
            return None

    async def fetchmany(self, size: int = 0) -> list[Row]:
        if not size:
            size = self.arraysize
        async with self._conn.lock:
            recs = await self._conn.wait(self._fetch_gen(size))
        self._pos += len(recs)
        return recs

    async def fetchall(self) -> list[Row]:
        async with self._conn.lock:
            recs = await self._conn.wait(self._fetch_gen(None))
        self._pos += len(recs)
        return recs

    async def __aiter__(self) -> AsyncIterator[Row]:
        while True:
            async with self._conn.lock:
                recs = await self._conn.wait(self._fetch_gen(self.itersize))
            for rec in recs:
                self._pos += 1
                yield rec
            if len(recs) < self.itersize:
                break

    async def scroll(self, value: int, mode: str = "relative") -> None:
        async with self._conn.lock:
            await self._conn.wait(self._scroll_gen(value, mode))
