"""
Psycopg connection object (async version)
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import logging
from time import monotonic
from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncGenerator, AsyncIterator, cast, overload
from contextlib import asynccontextmanager

from . import errors as e
from . import pq, waiting
from .abc import RV, AdaptContext, ConnDict, ConnParam, Params, PQGen, Query
from ._tpc import Xid
from .rows import AsyncRowFactory, Row, args_row, tuple_row
from .adapt import AdaptersMap
from ._enums import IsolationLevel
from ._compat import Self
from .conninfo import conninfo_attempts_async, conninfo_to_dict, make_conninfo
from .conninfo import timeout_from_conninfo
from ._pipeline import AsyncPipeline
from .generators import notifies
from .transaction import AsyncTransaction
from .cursor_async import AsyncCursor
from ._capabilities import capabilities
from .server_cursor import AsyncServerCursor
from ._connection_base import BaseConnection, CursorRow, Notify

if True:  # ASYNC
    import sys
    import asyncio
    from asyncio import Lock

    from ._compat import to_thread
else:
    from threading import Lock

if TYPE_CHECKING:
    from .pq.abc import PGconn

_WAIT_INTERVAL = 0.1

TEXT = pq.Format.TEXT
BINARY = pq.Format.BINARY

IDLE = pq.TransactionStatus.IDLE
ACTIVE = pq.TransactionStatus.ACTIVE
INTRANS = pq.TransactionStatus.INTRANS

if True:  # ASYNC
    _INTERRUPTED = (asyncio.CancelledError, KeyboardInterrupt)
else:
    _INTERRUPTED = KeyboardInterrupt

logger = logging.getLogger("psycopg")


class AsyncConnection(BaseConnection[Row]):
    """
    Wrapper for a connection to the database.
    """

    __module__ = "psycopg"

    cursor_factory: type[AsyncCursor[Row]]
    server_cursor_factory: type[AsyncServerCursor[Row]]
    row_factory: AsyncRowFactory[Row]
    _pipeline: AsyncPipeline | None

    def __init__(
        self,
        pgconn: PGconn,
        row_factory: AsyncRowFactory[Row] = cast(AsyncRowFactory[Row], tuple_row),
    ):
        super().__init__(pgconn)
        self.row_factory = row_factory
        self.lock = Lock()
        self.cursor_factory = AsyncCursor
        self.server_cursor_factory = AsyncServerCursor

    @classmethod
    async def connect(
        cls,
        conninfo: str = "",
        *,
        autocommit: bool = False,
        prepare_threshold: int | None = 5,
        context: AdaptContext | None = None,
        row_factory: AsyncRowFactory[Row] | None = None,
        cursor_factory: type[AsyncCursor[Row]] | None = None,
        **kwargs: ConnParam,
    ) -> Self:
        """
        Connect to a database server and return a new `AsyncConnection` instance.
        """
        if True:  # ASYNC
            if sys.platform == "win32":
                loop = asyncio.get_running_loop()
                if isinstance(loop, asyncio.ProactorEventLoop):
                    raise e.InterfaceError(
                        "Psycopg cannot use the 'ProactorEventLoop' to run in async"
                        " mode. Please use a compatible event loop, for instance by"
                        " setting 'asyncio.set_event_loop_policy"
                        "(WindowsSelectorEventLoopPolicy())'"
                    )

        params = await cls._get_connection_params(conninfo, **kwargs)
        timeout = timeout_from_conninfo(params)
        rv = None
        attempts = await conninfo_attempts_async(params)
        for attempt in attempts:
            try:
                conninfo = make_conninfo("", **attempt)
                gen = cls._connect_gen(conninfo, timeout=timeout)
                rv = await waiting.wait_conn_async(gen, interval=_WAIT_INTERVAL)
            except e._NO_TRACEBACK as ex:
                if len(attempts) > 1:
                    logger.debug(
                        "connection attempt failed: host: %r port: %r, hostaddr %r: %s",
                        attempt.get("host"),
                        attempt.get("port"),
                        attempt.get("hostaddr"),
                        str(ex),
                    )
                last_ex = ex
            else:
                break

        if not rv:
            assert last_ex
            raise last_ex.with_traceback(None)

        rv._autocommit = bool(autocommit)
        if row_factory:
            rv.row_factory = row_factory
        if cursor_factory:
            rv.cursor_factory = cursor_factory
        if context:
            rv._adapters = AdaptersMap(context.adapters)
        rv.prepare_threshold = prepare_threshold
        return rv

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.closed:
            return

        if exc_type:
            # try to rollback, but if there are problems (connection in a bad
            # state) just warn without clobbering the exception bubbling up.
            try:
                await self.rollback()
            except Exception as exc2:
                logger.warning("error ignored in rollback on %s: %s", self, exc2)
        else:
            await self.commit()

        # Close the connection only if it doesn't belong to a pool.
        if not getattr(self, "_pool", None):
            await self.close()

    @classmethod
    async def _get_connection_params(cls, conninfo: str, **kwargs: Any) -> ConnDict:
        """Manipulate connection parameters before connecting."""
        return conninfo_to_dict(conninfo, **kwargs)

    async def close(self) -> None:
        """Close the database connection."""
        if self.closed:
            return
        self._closed = True

        # TODO: maybe send a cancel on close, if the connection is ACTIVE?

        self.pgconn.finish()

    @overload
    def cursor(self, *, binary: bool = False) -> AsyncCursor[Row]: ...

    @overload
    def cursor(
        self, *, binary: bool = False, row_factory: AsyncRowFactory[CursorRow]
    ) -> AsyncCursor[CursorRow]: ...

    @overload
    def cursor(
        self,
        name: str,
        *,
        binary: bool = False,
        scrollable: bool | None = None,
        withhold: bool = False,
    ) -> AsyncServerCursor[Row]: ...

    @overload
    def cursor(
        self,
        name: str,
        *,
        binary: bool = False,
        row_factory: AsyncRowFactory[CursorRow],
        scrollable: bool | None = None,
        withhold: bool = False,
    ) -> AsyncServerCursor[CursorRow]: ...

    def cursor(
        self,
        name: str = "",
        *,
        binary: bool = False,
        row_factory: AsyncRowFactory[Any] | None = None,
        scrollable: bool | None = None,
        withhold: bool = False,
    ) -> AsyncCursor[Any] | AsyncServerCursor[Any]:
        """
        Return a new `AsyncCursor` to send commands and queries to the connection.
        """
        self._check_connection_ok()

        if not row_factory:
            row_factory = self.row_factory

        cur: AsyncCursor[Any] | AsyncServerCursor[Any]
        if name:
            cur = self.server_cursor_factory(
                self,
                name=name,
                row_factory=row_factory,
                scrollable=scrollable,
                withhold=withhold,
            )
        else:
            cur = self.cursor_factory(self, row_factory=row_factory)

        if binary:
            cur.format = BINARY

        return cur

    async def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        prepare: bool | None = None,
        binary: bool = False,
    ) -> AsyncCursor[Row]:
        """Execute a query and return a cursor to read its results."""
        try:
            cur = self.cursor()
            if binary:
                cur.format = BINARY

            return await cur.execute(query, params, prepare=prepare)

        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)

    async def commit(self) -> None:
        """Commit any pending transaction to the database."""
        async with self.lock:
            await self.wait(self._commit_gen())

    async def rollback(self) -> None:
        """Roll back to the start of any pending transaction."""
        async with self.lock:
            await self.wait(self._rollback_gen())

    async def cancel_safe(self, *, timeout: float = 30.0) -> None:
        """Cancel the current operation on the connection.

        :param timeout: raise a `~errors.CancellationTimeout` if the
            cancellation request does not succeed within `timeout` seconds.

        Note that a successful cancel attempt on the client is not a guarantee
        that the server will successfully manage to cancel the operation.

        This is a non-blocking version of `~Connection.cancel()` which
        leverages a more secure and improved cancellation feature of the libpq,
        which is only available from version 17.

        If the underlying libpq is older than version 17, the method will fall
        back to using the same implementation of `!cancel()`.
        """
        if not self._should_cancel():
            return

        if capabilities.has_cancel_safe():
            await waiting.wait_conn_async(
                self._cancel_gen(timeout=timeout), interval=_WAIT_INTERVAL
            )
        else:
            if True:  # ASYNC
                await to_thread(self.cancel)
            else:
                self.cancel()

    async def _try_cancel(self, *, timeout: float = 5.0) -> None:
        try:
            await self.cancel_safe(timeout=timeout)
        except Exception as ex:
            logger.warning("query cancellation failed: %s", ex)

    @asynccontextmanager
    async def transaction(
        self, savepoint_name: str | None = None, force_rollback: bool = False
    ) -> AsyncIterator[AsyncTransaction]:
        """
        Start a context block with a new transaction or nested transaction.

        :param savepoint_name: Name of the savepoint used to manage a nested
            transaction. If `!None`, one will be chosen automatically.
        :param force_rollback: Roll back the transaction at the end of the
            block even if there were no error (e.g. to try a no-op process).
        :rtype: AsyncTransaction
        """
        tx = AsyncTransaction(self, savepoint_name, force_rollback)
        if self._pipeline:
            async with self.pipeline(), tx, self.pipeline():
                yield tx
        else:
            async with tx:
                yield tx

    async def notifies(
        self, *, timeout: float | None = None, stop_after: int | None = None
    ) -> AsyncGenerator[Notify, None]:
        """
        Yield `Notify` objects as soon as they are received from the database.

        :param timeout: maximum amount of time to wait for notifications.
            `!None` means no timeout.
        :param stop_after: stop after receiving this number of notifications.
            You might actually receive more than this number if more than one
            notifications arrives in the same packet.
        """
        # Allow interrupting the wait with a signal by reducing a long timeout
        # into shorter intervals.
        if timeout is not None:
            deadline = monotonic() + timeout
            interval = min(timeout, _WAIT_INTERVAL)
        else:
            deadline = None
            interval = _WAIT_INTERVAL

        nreceived = 0

        async with self.lock:
            enc = self.pgconn._encoding

            # Remove the backlog deque for the duration of this critical
            # section to avoid reporting notifies twice.
            self._notifies_backlog, d = None, self._notifies_backlog

            try:
                while True:
                    # if notifies were received when the generator was off,
                    # return them in a first batch.
                    if d:
                        while d:
                            yield d.popleft()
                            nreceived += 1
                    else:
                        try:
                            pgns = await self.wait(
                                notifies(self.pgconn), interval=interval
                            )
                        except e._NO_TRACEBACK as ex:
                            raise ex.with_traceback(None)

                        # Emit the notifications received.
                        for pgn in pgns:
                            yield Notify(
                                pgn.relname.decode(enc),
                                pgn.extra.decode(enc),
                                pgn.be_pid,
                            )
                            nreceived += 1

                    # Stop if we have received enough notifications.
                    if stop_after is not None and nreceived >= stop_after:
                        break

                    # Check the deadline after the loop to ensure that timeout=0
                    # polls at least once.
                    if deadline:
                        interval = min(_WAIT_INTERVAL, deadline - monotonic())
                        if interval < 0.0:
                            break
            finally:
                self._notifies_backlog = d

    @asynccontextmanager
    async def pipeline(self) -> AsyncIterator[AsyncPipeline]:
        """Context manager to switch the connection into pipeline mode."""
        async with self.lock:
            self._check_connection_ok()

            pipeline = self._pipeline
            if pipeline is None:
                # WARNING: reference loop, broken ahead.
                pipeline = self._pipeline = AsyncPipeline(self)

        try:
            async with pipeline:
                yield pipeline
        finally:
            if pipeline.level == 0:
                async with self.lock:
                    assert pipeline is self._pipeline
                    self._pipeline = None

    async def wait(self, gen: PQGen[RV], interval: float | None = _WAIT_INTERVAL) -> RV:
        """
        Consume a generator operating on the connection.

        The function must be used on generators that don't change connection
        fd (i.e. not on connect and reset).
        """
        try:
            return await waiting.wait_async(gen, self.pgconn.socket, interval=interval)
        except _INTERRUPTED:
            if self.pgconn.transaction_status == ACTIVE:
                # On Ctrl-C, try to cancel the query in the server, otherwise
                # the connection will remain stuck in ACTIVE state.
                await self._try_cancel(timeout=5.0)
                try:
                    await waiting.wait_async(gen, self.pgconn.socket, interval=interval)
                except e.QueryCanceled:
                    pass  # as expected
            raise

    def _set_autocommit(self, value: bool) -> None:
        if True:  # ASYNC
            self._no_set_async("autocommit")
        else:
            self.set_autocommit(value)

    async def set_autocommit(self, value: bool) -> None:
        """Method version of the `~Connection.autocommit` setter."""
        async with self.lock:
            await self.wait(self._set_autocommit_gen(value))

    def _set_isolation_level(self, value: IsolationLevel | None) -> None:
        if True:  # ASYNC
            self._no_set_async("isolation_level")
        else:
            self.set_isolation_level(value)

    async def set_isolation_level(self, value: IsolationLevel | None) -> None:
        """Method version of the `~Connection.isolation_level` setter."""
        async with self.lock:
            await self.wait(self._set_isolation_level_gen(value))

    def _set_read_only(self, value: bool | None) -> None:
        if True:  # ASYNC
            self._no_set_async("read_only")
        else:
            self.set_read_only(value)

    async def set_read_only(self, value: bool | None) -> None:
        """Method version of the `~Connection.read_only` setter."""
        async with self.lock:
            await self.wait(self._set_read_only_gen(value))

    def _set_deferrable(self, value: bool | None) -> None:
        if True:  # ASYNC
            self._no_set_async("deferrable")
        else:
            self.set_deferrable(value)

    async def set_deferrable(self, value: bool | None) -> None:
        """Method version of the `~Connection.deferrable` setter."""
        async with self.lock:
            await self.wait(self._set_deferrable_gen(value))

    if True:  # ASYNC

        def _no_set_async(self, attribute: str) -> None:
            raise AttributeError(
                f"'the {attribute!r} property is read-only on async connections:"
                f" please use 'await .set_{attribute}()' instead."
            )

    async def tpc_begin(self, xid: Xid | str) -> None:
        """
        Begin a TPC transaction with the given transaction ID `!xid`.
        """
        async with self.lock:
            await self.wait(self._tpc_begin_gen(xid))

    async def tpc_prepare(self) -> None:
        """
        Perform the first phase of a transaction started with `tpc_begin()`.
        """
        try:
            async with self.lock:
                await self.wait(self._tpc_prepare_gen())
        except e.ObjectNotInPrerequisiteState as ex:
            raise e.NotSupportedError(str(ex)) from None

    async def tpc_commit(self, xid: Xid | str | None = None) -> None:
        """
        Commit a prepared two-phase transaction.
        """
        async with self.lock:
            await self.wait(self._tpc_finish_gen("COMMIT", xid))

    async def tpc_rollback(self, xid: Xid | str | None = None) -> None:
        """
        Roll back a prepared two-phase transaction.
        """
        async with self.lock:
            await self.wait(self._tpc_finish_gen("ROLLBACK", xid))

    async def tpc_recover(self) -> list[Xid]:
        self._check_tpc()
        status = self.info.transaction_status
        async with self.cursor(row_factory=args_row(Xid._from_record)) as cur:
            await cur.execute(Xid._get_recover_query())
            res = await cur.fetchall()

        if status == IDLE and self.info.transaction_status == INTRANS:
            await self.rollback()

        return res
