"""
commands pipeline management
"""

# Copyright (C) 2021 The Psycopg Team

from __future__ import annotations

import logging
from types import TracebackType
from typing import TYPE_CHECKING, Any

from . import errors as e
from . import pq
from .abc import PipelineCommand, PQGen
from ._compat import Deque, Self, TypeAlias
from .pq.misc import connection_summary
from .generators import fetch_many, pipeline_communicate, send
from ._capabilities import capabilities

if TYPE_CHECKING:
    from .pq.abc import PGresult
    from ._preparing import Key, Prepare  # noqa: F401
    from .connection import Connection
    from ._cursor_base import BaseCursor  # noqa: F401
    from ._connection_base import BaseConnection
    from .connection_async import AsyncConnection


PendingResult: TypeAlias = (
    "tuple[BaseCursor[Any, Any], tuple[Key, Prepare, bytes] | None] | None"
)

FATAL_ERROR = pq.ExecStatus.FATAL_ERROR
PIPELINE_ABORTED = pq.ExecStatus.PIPELINE_ABORTED
BAD = pq.ConnStatus.BAD

ACTIVE = pq.TransactionStatus.ACTIVE

logger = logging.getLogger("psycopg")


class BasePipeline:
    command_queue: Deque[PipelineCommand]
    result_queue: Deque[PendingResult]

    def __init__(self, conn: BaseConnection[Any]) -> None:
        self._conn = conn
        self.pgconn = conn.pgconn
        self.command_queue = Deque[PipelineCommand]()
        self.result_queue = Deque[PendingResult]()
        self.level = 0

    def __repr__(self) -> str:
        cls = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        info = connection_summary(self._conn.pgconn)
        return f"<{cls} {info} at 0x{id(self):x}>"

    @property
    def status(self) -> pq.PipelineStatus:
        return pq.PipelineStatus(self.pgconn.pipeline_status)

    @classmethod
    def is_supported(cls) -> bool:
        """Return `!True` if the psycopg libpq wrapper supports pipeline mode."""
        return capabilities.has_pipeline()

    def _enter_gen(self) -> PQGen[None]:
        capabilities.has_pipeline(check=True)
        if self.level == 0:
            self.pgconn.enter_pipeline_mode()
        elif self.command_queue or self.pgconn.transaction_status == ACTIVE:
            # Nested pipeline case.
            #  Transaction might be ACTIVE when the pipeline uses an "implicit
            #  transaction", typically in autocommit mode. But when entering a
            #  Psycopg transaction(), we expect the IDLE state. By sync()-ing,
            #  we make sure all previous commands are completed and the
            #  transaction gets back to IDLE.
            yield from self._sync_gen()
        self.level += 1

    def _exit(self, exc: BaseException | None) -> None:
        self.level -= 1
        if self.level == 0 and self.pgconn.status != BAD:
            try:
                self.pgconn.exit_pipeline_mode()
            except e.OperationalError as exc2:
                # Notice that this error might be pretty irrecoverable. It
                # happens on COPY, for instance: even if sync succeeds, exiting
                # fails with "cannot exit pipeline mode with uncollected results"
                if exc:
                    logger.warning("error ignored exiting %r: %s", self, exc2)
                else:
                    raise exc2.with_traceback(None)

    def _sync_gen(self) -> PQGen[None]:
        self._enqueue_sync()
        yield from self._communicate_gen()
        yield from self._fetch_gen(flush=False)

    def _exit_gen(self) -> PQGen[None]:
        """
        Exit current pipeline by sending a Sync and fetch back all remaining results.
        """
        try:
            self._enqueue_sync()
            yield from self._communicate_gen()
        finally:
            yield from self._fetch_gen(flush=True)

    def _communicate_gen(self) -> PQGen[None]:
        """Communicate with pipeline to send commands and possibly fetch
        results, which are then processed.
        """
        fetched = yield from pipeline_communicate(self.pgconn, self.command_queue)
        exception = None
        for results in fetched:
            queued = self.result_queue.popleft()
            try:
                self._process_results(queued, results)
            except e.Error as exc:
                if exception is None:
                    exception = exc
        if exception is not None:
            raise exception

    def _fetch_gen(self, *, flush: bool) -> PQGen[None]:
        """Fetch available results from the connection and process them with
        pipeline queued items.

        If 'flush' is True, a PQsendFlushRequest() is issued in order to make
        sure results can be fetched. Otherwise, the caller may emit a
        PQpipelineSync() call to ensure the output buffer gets flushed before
        fetching.
        """
        if not self.result_queue:
            return

        if flush:
            self.pgconn.send_flush_request()
            yield from send(self.pgconn)

        exception = None
        while self.result_queue:
            results = yield from fetch_many(self.pgconn)
            if not results:
                # No more results to fetch, but there may still be pending
                # commands.
                break
            queued = self.result_queue.popleft()
            try:
                self._process_results(queued, results)
            except e.Error as exc:
                if exception is None:
                    exception = exc
        if exception is not None:
            raise exception

    def _process_results(self, queued: PendingResult, results: list[PGresult]) -> None:
        """Process a results set fetched from the current pipeline.

        This matches 'results' with its respective element in the pipeline
        queue. For commands (None value in the pipeline queue), results are
        checked directly. For prepare statement creation requests, update the
        cache. Otherwise, results are attached to their respective cursor.
        """
        if queued is None:
            (result,) = results
            if result.status == FATAL_ERROR:
                raise e.error_from_result(result, encoding=self.pgconn._encoding)
            elif result.status == PIPELINE_ABORTED:
                raise e.PipelineAborted("pipeline aborted")
        else:
            cursor, prepinfo = queued
            if prepinfo:
                key, prep, name = prepinfo
                # Update the prepare state of the query.
                cursor._conn._prepared.validate(key, prep, name, results)
            cursor._check_results(results)
            cursor._set_results(results)

    def _enqueue_sync(self) -> None:
        """Enqueue a PQpipelineSync() command."""
        self.command_queue.append(self.pgconn.pipeline_sync)
        self.result_queue.append(None)


class Pipeline(BasePipeline):
    """Handler for connection in pipeline mode."""

    __module__ = "psycopg"
    _conn: Connection[Any]

    def __init__(self, conn: Connection[Any]) -> None:
        super().__init__(conn)

    def sync(self) -> None:
        """Sync the pipeline, send any pending command and receive and process
        all available results.
        """
        try:
            with self._conn.lock:
                self._conn.wait(self._sync_gen())
        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)

    def __enter__(self) -> Self:
        with self._conn.lock:
            self._conn.wait(self._enter_gen())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            with self._conn.lock:
                self._conn.wait(self._exit_gen())
        except Exception as exc2:
            # Don't clobber an exception raised in the block with this one
            if exc_val:
                logger.warning("error ignored terminating %r: %s", self, exc2)
            else:
                raise exc2.with_traceback(None)
        finally:
            self._exit(exc_val)


class AsyncPipeline(BasePipeline):
    """Handler for async connection in pipeline mode."""

    __module__ = "psycopg"
    _conn: AsyncConnection[Any]

    def __init__(self, conn: AsyncConnection[Any]) -> None:
        super().__init__(conn)

    async def sync(self) -> None:
        try:
            async with self._conn.lock:
                await self._conn.wait(self._sync_gen())
        except e._NO_TRACEBACK as ex:
            raise ex.with_traceback(None)

    async def __aenter__(self) -> Self:
        async with self._conn.lock:
            await self._conn.wait(self._enter_gen())
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            async with self._conn.lock:
                await self._conn.wait(self._exit_gen())
        except Exception as exc2:
            # Don't clobber an exception raised in the block with this one
            if exc_val:
                logger.warning("error ignored terminating %r: %s", self, exc2)
            else:
                raise exc2.with_traceback(None)
        finally:
            self._exit(exc_val)
