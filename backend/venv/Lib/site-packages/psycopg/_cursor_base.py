"""
Psycopg BaseCursor object
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterable, NoReturn, Sequence
from functools import partial

from . import adapt
from . import errors as e
from . import pq
from .abc import ConnectionType, Params, PQGen, Query
from .rows import Row, RowMaker
from ._column import Column
from .pq.misc import connection_summary
from ._queries import PostgresClientQuery, PostgresQuery
from ._preparing import Prepare
from .generators import execute, fetch, send
from ._capabilities import capabilities

if TYPE_CHECKING:
    from .abc import Transformer
    from .pq.abc import PGconn, PGresult

TEXT = pq.Format.TEXT
BINARY = pq.Format.BINARY

EMPTY_QUERY = pq.ExecStatus.EMPTY_QUERY
COMMAND_OK = pq.ExecStatus.COMMAND_OK
TUPLES_OK = pq.ExecStatus.TUPLES_OK
COPY_OUT = pq.ExecStatus.COPY_OUT
COPY_IN = pq.ExecStatus.COPY_IN
COPY_BOTH = pq.ExecStatus.COPY_BOTH
FATAL_ERROR = pq.ExecStatus.FATAL_ERROR
SINGLE_TUPLE = pq.ExecStatus.SINGLE_TUPLE
TUPLES_CHUNK = pq.ExecStatus.TUPLES_CHUNK
PIPELINE_ABORTED = pq.ExecStatus.PIPELINE_ABORTED

ACTIVE = pq.TransactionStatus.ACTIVE


class BaseCursor(Generic[ConnectionType, Row]):
    __slots__ = """
        _conn format _adapters arraysize _closed _results pgresult _pos
        _iresult _rowcount _query _tx _last_query _row_factory _make_row
        _pgconn _execmany_returning
        __weakref__
        """.split()

    _tx: Transformer
    _make_row: RowMaker[Row]
    _pgconn: PGconn
    _query_cls: type[PostgresQuery] = PostgresQuery

    def __init__(self, connection: ConnectionType):
        self._conn = connection
        self.format = TEXT
        self._pgconn = connection.pgconn
        self._adapters = adapt.AdaptersMap(connection.adapters)
        self.arraysize = 1
        self._closed = False
        self._last_query: Query | None = None
        self._reset()

    def _reset(self, reset_query: bool = True) -> None:
        self._results: list[PGresult] = []
        self.pgresult: PGresult | None = None
        self._pos = 0
        self._iresult = 0
        self._rowcount = -1
        self._query: PostgresQuery | None
        # None if executemany() not executing, True/False according to returning state
        self._execmany_returning: bool | None = None
        if reset_query:
            self._query = None

    def __repr__(self) -> str:
        cls = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        info = connection_summary(self._pgconn)
        if self._closed:
            status = "closed"
        elif self.pgresult:
            status = pq.ExecStatus(self.pgresult.status).name
        else:
            status = "no result"
        return f"<{cls} [{status}] {info} at 0x{id(self):x}>"

    @property
    def connection(self) -> ConnectionType:
        """The connection this cursor is using."""
        return self._conn

    @property
    def adapters(self) -> adapt.AdaptersMap:
        return self._adapters

    @property
    def closed(self) -> bool:
        """`True` if the cursor is closed."""
        return self._closed

    @property
    def description(self) -> list[Column] | None:
        """
        A list of `Column` objects describing the current resultset.

        `!None` if the current resultset didn't return tuples.
        """
        res = self.pgresult

        # We return columns if we have nfields, but also if we don't but
        # the query said we got tuples (mostly to handle the super useful
        # query "SELECT ;"
        if res and (
            res.nfields
            or res.status == TUPLES_OK
            or res.status == SINGLE_TUPLE
            or res.status == TUPLES_CHUNK
        ):
            return [Column(self, i) for i in range(res.nfields)]
        else:
            return None

    @property
    def rowcount(self) -> int:
        """Number of records affected by the precedent operation."""
        return self._rowcount

    @property
    def rownumber(self) -> int | None:
        """Index of the next row to fetch in the current result.

        `!None` if there is no result to fetch.
        """
        tuples = self.pgresult and self.pgresult.status == TUPLES_OK
        return self._pos if tuples else None

    def setinputsizes(self, sizes: Sequence[Any]) -> None:
        # no-op
        pass

    def setoutputsize(self, size: Any, column: int | None = None) -> None:
        # no-op
        pass

    def nextset(self) -> bool | None:
        """
        Move to the result set of the next query executed through `executemany()`
        or to the next result set if `execute()` returned more than one.

        Return `!True` if a new result is available, which will be the one
        methods `!fetch*()` will operate on.
        """
        if self._iresult < len(self._results) - 1:
            self._select_current_result(self._iresult + 1)
            return True
        else:
            return None

    @property
    def statusmessage(self) -> str | None:
        """
        The command status tag from the last SQL command executed.

        `!None` if the cursor doesn't have a result available.
        """
        msg = self.pgresult.command_status if self.pgresult else None
        return msg.decode() if msg else None

    def _make_row_maker(self) -> RowMaker[Row]:
        raise NotImplementedError

    #
    # Generators for the high level operations on the cursor
    #
    # Like for sync/async connections, these are implemented as generators
    # so that different concurrency strategies (threads,asyncio) can use their
    # own way of waiting (or better, `connection.wait()`).
    #

    def _execute_gen(
        self,
        query: Query,
        params: Params | None = None,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
    ) -> PQGen[None]:
        """Generator implementing `Cursor.execute()`."""
        yield from self._start_query(query)
        pgq = self._convert_query(query, params)
        yield from self._maybe_prepare_gen(pgq, prepare=prepare, binary=binary)
        if self._conn._pipeline:
            yield from self._conn._pipeline._communicate_gen()

        self._last_query = query
        yield from self._conn._prepared.maintain_gen(self._conn)

    def _executemany_gen_pipeline(
        self, query: Query, params_seq: Iterable[Params], returning: bool
    ) -> PQGen[None]:
        """
        Generator implementing `Cursor.executemany()` with pipelines available.
        """
        pipeline = self._conn._pipeline
        assert pipeline

        yield from self._start_query(query)
        if not returning:
            self._rowcount = 0

        assert self._execmany_returning is None
        self._execmany_returning = returning

        first = True
        for params in params_seq:
            if first:
                pgq = self._convert_query(query, params)
                self._query = pgq
                first = False
            else:
                pgq.dump(params)

            yield from self._maybe_prepare_gen(pgq, prepare=True)
            yield from pipeline._communicate_gen()

        self._last_query = query

        if returning:
            yield from pipeline._fetch_gen(flush=True)

        yield from self._conn._prepared.maintain_gen(self._conn)

    def _executemany_gen_no_pipeline(
        self, query: Query, params_seq: Iterable[Params], returning: bool
    ) -> PQGen[None]:
        """
        Generator implementing `Cursor.executemany()` with pipelines not available.
        """
        yield from self._start_query(query)
        if not returning:
            self._rowcount = 0

        assert self._execmany_returning is None
        self._execmany_returning = returning

        first = True
        for params in params_seq:
            if first:
                pgq = self._convert_query(query, params)
                self._query = pgq
                first = False
            else:
                pgq.dump(params)

            yield from self._maybe_prepare_gen(pgq, prepare=True)

        self._last_query = query
        yield from self._conn._prepared.maintain_gen(self._conn)

    def _maybe_prepare_gen(
        self,
        pgq: PostgresQuery,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
    ) -> PQGen[None]:
        # Check if the query is prepared or needs preparing
        prep, name = self._get_prepared(pgq, prepare)
        if prep is Prepare.NO:
            # The query must be executed without preparing
            self._execute_send(pgq, binary=binary)
        else:
            # If the query is not already prepared, prepare it.
            if prep is Prepare.SHOULD:
                self._send_prepare(name, pgq)
                if not self._conn._pipeline:
                    (result,) = yield from execute(self._pgconn)
                    if result.status == FATAL_ERROR:
                        raise e.error_from_result(result, encoding=self._encoding)
            # Then execute it.
            self._send_query_prepared(name, pgq, binary=binary)

        # Update the prepare state of the query.
        # If an operation requires to flush our prepared statements cache,
        # it will be added to the maintenance commands to execute later.
        key = self._conn._prepared.maybe_add_to_cache(pgq, prep, name)

        if self._conn._pipeline:
            queued = None
            if key is not None:
                queued = (key, prep, name)
            self._conn._pipeline.result_queue.append((self, queued))
            return

        # run the query
        results = yield from execute(self._pgconn)

        if key is not None:
            self._conn._prepared.validate(key, prep, name, results)

        self._check_results(results)
        self._set_results(results)

    def _get_prepared(
        self, pgq: PostgresQuery, prepare: bool | None = None
    ) -> tuple[Prepare, bytes]:
        return self._conn._prepared.get(pgq, prepare)

    def _stream_send_gen(
        self,
        query: Query,
        params: Params | None = None,
        *,
        binary: bool | None = None,
        size: int,
    ) -> PQGen[None]:
        """Generator to send the query for `Cursor.stream()`."""
        yield from self._start_query(query)
        pgq = self._convert_query(query, params)
        self._execute_send(pgq, binary=binary, force_extended=True)
        if size < 1:
            raise ValueError("size must be >= 1")
        elif size == 1:
            self._pgconn.set_single_row_mode()
        else:
            capabilities.has_stream_chunked(check=True)
            self._pgconn.set_chunked_rows_mode(size)
        self._last_query = query
        yield from send(self._pgconn)

    def _stream_fetchone_gen(self, first: bool) -> PQGen[PGresult | None]:
        res: PGresult | None = yield from fetch(self._pgconn)
        if res is None:
            return None

        status = res.status
        if status == SINGLE_TUPLE or status == TUPLES_CHUNK:
            self.pgresult = res
            self._tx.set_pgresult(res, set_loaders=first)
            if first:
                self._make_row = self._make_row_maker()
            return res

        elif status == TUPLES_OK or status == COMMAND_OK:
            # End of single row results
            while res:
                res = yield from fetch(self._pgconn)
            if status != TUPLES_OK:
                raise e.ProgrammingError(
                    "the operation in stream() didn't produce a result"
                )
            return None

        else:
            # Errors, unexpected values
            return self._raise_for_result(res)

    def _start_query(self, query: Query | None = None) -> PQGen[None]:
        """Generator to start the processing of a query.

        It is implemented as generator because it may send additional queries,
        such as `begin`.
        """
        if self.closed:
            raise e.InterfaceError("the cursor is closed")

        self._reset()
        if not self._last_query or (self._last_query is not query):
            self._last_query = None
            self._tx = adapt.Transformer(self)
        yield from self._conn._start_query()

    def _start_copy_gen(
        self, statement: Query, params: Params | None = None
    ) -> PQGen[None]:
        """Generator implementing sending a command for `Cursor.copy()."""

        # The connection gets in an unrecoverable state if we attempt COPY in
        # pipeline mode. Forbid it explicitly.
        if self._conn._pipeline:
            raise e.NotSupportedError("COPY cannot be used in pipeline mode")

        yield from self._start_query()

        # Merge the params client-side
        if params:
            pgq = PostgresClientQuery(self._tx)
            pgq.convert(statement, params)
            statement = pgq.query

        query = self._convert_query(statement)

        self._execute_send(query, binary=False)
        results = yield from execute(self._pgconn)
        if len(results) != 1:
            raise e.ProgrammingError("COPY cannot be mixed with other operations")

        self._check_copy_result(results[0])
        self._set_results(results)

    def _execute_send(
        self,
        query: PostgresQuery,
        *,
        force_extended: bool = False,
        binary: bool | None = None,
    ) -> None:
        """
        Implement part of execute() before waiting common to sync and async.

        This is not a generator, but a normal non-blocking function.
        """
        if binary is None:
            fmt = self.format
        else:
            fmt = BINARY if binary else TEXT

        self._query = query

        if self._conn._pipeline:
            # In pipeline mode always use PQsendQueryParams - see #314
            # Multiple statements in the same query are not allowed anyway.
            self._conn._pipeline.command_queue.append(
                partial(
                    self._pgconn.send_query_params,
                    query.query,
                    query.params,
                    param_formats=query.formats,
                    param_types=query.types,
                    result_format=fmt,
                )
            )
        elif force_extended or query.params or fmt == BINARY:
            self._pgconn.send_query_params(
                query.query,
                query.params,
                param_formats=query.formats,
                param_types=query.types,
                result_format=fmt,
            )
        else:
            # If we can, let's use simple query protocol,
            # as it can execute more than one statement in a single query.
            self._pgconn.send_query(query.query)

    def _convert_query(
        self, query: Query, params: Params | None = None
    ) -> PostgresQuery:
        pgq = self._query_cls(self._tx)
        pgq.convert(query, params)
        return pgq

    def _check_results(self, results: list[PGresult]) -> None:
        """
        Verify that the results of a query are valid.

        Verify that the query returned at least one result and that they all
        represent a valid result from the database.
        """
        if not results:
            raise e.InternalError("got no result from the query")

        for res in results:
            status = res.status
            if status != TUPLES_OK and status != COMMAND_OK and status != EMPTY_QUERY:
                self._raise_for_result(res)

    def _raise_for_result(self, result: PGresult) -> NoReturn:
        """
        Raise an appropriate error message for an unexpected database result
        """
        status = result.status
        if status == FATAL_ERROR:
            raise e.error_from_result(result, encoding=self._encoding)
        elif status == PIPELINE_ABORTED:
            raise e.PipelineAborted("pipeline aborted")
        elif status == COPY_IN or status == COPY_OUT or status == COPY_BOTH:
            raise e.ProgrammingError(
                "COPY cannot be used with this method; use copy() instead"
            )
        else:
            raise e.InternalError(
                "unexpected result status from query:" f" {pq.ExecStatus(status).name}"
            )

    def _select_current_result(self, i: int, format: pq.Format | None = None) -> None:
        """
        Select one of the results in the cursor as the active one.
        """
        self._iresult = i
        res = self.pgresult = self._results[i]

        # Note: the only reason to override format is to correctly set
        # binary loaders on server-side cursors, because send_describe_portal
        # only returns a text result.
        self._tx.set_pgresult(res, format=format)

        self._pos = 0

        if res.status == TUPLES_OK:
            self._rowcount = self.pgresult.ntuples

        # COPY_OUT has never info about nrows. We need such result for the
        # columns in order to return a `description`, but not overwrite the
        # cursor rowcount (which was set by the Copy object).
        elif res.status != COPY_OUT:
            nrows = self.pgresult.command_tuples
            self._rowcount = nrows if nrows is not None else -1

        self._make_row = self._make_row_maker()

    def _set_results(self, results: list[PGresult]) -> None:
        if self._execmany_returning is None:
            # Received from execute()
            self._results[:] = results
            self._select_current_result(0)

        else:
            # Received from executemany()
            if self._execmany_returning:
                first_batch = not self._results
                self._results.extend(results)
                if first_batch:
                    self._select_current_result(0)
            else:
                # In non-returning case, set rowcount to the cumulated number of
                # rows of executed queries.
                for res in results:
                    self._rowcount += res.command_tuples or 0

    def _send_prepare(self, name: bytes, query: PostgresQuery) -> None:
        if self._conn._pipeline:
            self._conn._pipeline.command_queue.append(
                partial(
                    self._pgconn.send_prepare,
                    name,
                    query.query,
                    param_types=query.types,
                )
            )
            self._conn._pipeline.result_queue.append(None)
        else:
            self._pgconn.send_prepare(name, query.query, param_types=query.types)

    def _send_query_prepared(
        self, name: bytes, pgq: PostgresQuery, *, binary: bool | None = None
    ) -> None:
        if binary is None:
            fmt = self.format
        else:
            fmt = BINARY if binary else TEXT

        if self._conn._pipeline:
            self._conn._pipeline.command_queue.append(
                partial(
                    self._pgconn.send_query_prepared,
                    name,
                    pgq.params,
                    param_formats=pgq.formats,
                    result_format=fmt,
                )
            )
        else:
            self._pgconn.send_query_prepared(
                name, pgq.params, param_formats=pgq.formats, result_format=fmt
            )

    def _check_result_for_fetch(self) -> None:
        if self.closed:
            raise e.InterfaceError("the cursor is closed")
        res = self.pgresult
        if not res:
            raise e.ProgrammingError("no result available")

        status = res.status
        if status == TUPLES_OK:
            return
        elif status == FATAL_ERROR:
            raise e.error_from_result(res, encoding=self._encoding)
        elif status == PIPELINE_ABORTED:
            raise e.PipelineAborted("pipeline aborted")
        else:
            raise e.ProgrammingError("the last operation didn't produce a result")

    def _check_copy_result(self, result: PGresult) -> None:
        """
        Check that the value returned in a copy() operation is a legit COPY.
        """
        status = result.status
        if status == COPY_IN or status == COPY_OUT:
            return
        elif status == FATAL_ERROR:
            raise e.error_from_result(result, encoding=self._encoding)
        else:
            raise e.ProgrammingError(
                "copy() should be used only with COPY ... TO STDOUT or COPY ..."
                f" FROM STDIN statements, got {pq.ExecStatus(status).name}"
            )

    def _scroll(self, value: int, mode: str) -> None:
        self._check_result_for_fetch()
        assert self.pgresult
        if mode == "relative":
            newpos = self._pos + value
        elif mode == "absolute":
            newpos = value
        else:
            raise ValueError(f"bad mode: {mode}. It should be 'relative' or 'absolute'")
        if not 0 <= newpos < self.pgresult.ntuples:
            raise IndexError("position out of bound")
        self._pos = newpos

    def _close(self) -> None:
        """Non-blocking part of closing. Common to sync/async."""
        # Don't reset the query because it may be useful to investigate after
        # an error.
        self._reset(reset_query=False)
        self._closed = True

    @property
    def _encoding(self) -> str:
        return self._pgconn._encoding
