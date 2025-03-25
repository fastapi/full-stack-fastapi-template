"""
Generators implementing communication protocols with the libpq

Certain operations (connection, querying) are an interleave of libpq calls and
waiting for the socket to be ready. This module contains the code to execute
the operations, yielding a polling state whenever there is to wait. The
functions in the `waiting` module are the ones who wait more or less
cooperatively for the socket to be ready and make these generators continue.

These generators yield `Wait` objects whenever an operation would block. These
generators assume the connection fileno will not change. In case of the
connection function, where the fileno may change, the generators yield pairs
(fileno, `Wait`).

The generator can be restarted sending the appropriate `Ready` state when the
file descriptor is ready. If a None value is sent, it means that the wait
function timed out without any file descriptor becoming ready; in this case the
generator should probably yield the same value again in order to wait more.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import logging
from time import monotonic

from . import errors as e
from . import pq
from .abc import Buffer, PipelineCommand, PQGen, PQGenConn
from .pq.abc import PGcancelConn, PGconn, PGresult
from ._compat import Deque
from .waiting import Ready, Wait
from ._cmodule import _psycopg
from ._encodings import conninfo_encoding

OK = pq.ConnStatus.OK
BAD = pq.ConnStatus.BAD

POLL_OK = pq.PollingStatus.OK
POLL_READING = pq.PollingStatus.READING
POLL_WRITING = pq.PollingStatus.WRITING
POLL_FAILED = pq.PollingStatus.FAILED

COMMAND_OK = pq.ExecStatus.COMMAND_OK
COPY_OUT = pq.ExecStatus.COPY_OUT
COPY_IN = pq.ExecStatus.COPY_IN
COPY_BOTH = pq.ExecStatus.COPY_BOTH
FATAL_ERROR = pq.ExecStatus.FATAL_ERROR
PIPELINE_SYNC = pq.ExecStatus.PIPELINE_SYNC

WAIT_R = Wait.R
WAIT_W = Wait.W
WAIT_RW = Wait.RW
READY_R = Ready.R
READY_W = Ready.W
READY_RW = Ready.RW

logger = logging.getLogger(__name__)


def _connect(conninfo: str, *, timeout: float = 0.0) -> PQGenConn[PGconn]:
    """
    Generator to create a database connection without blocking.
    """
    deadline = monotonic() + timeout if timeout else 0.0

    conn = pq.PGconn.connect_start(conninfo.encode())
    while True:
        if conn.status == BAD:
            encoding = conninfo_encoding(conninfo)
            raise e.OperationalError(
                f"connection is bad: {conn.get_error_message(encoding)}",
                pgconn=conn,
            )

        status = conn.connect_poll()

        if status == POLL_READING or status == POLL_WRITING:
            wait = WAIT_R if status == POLL_READING else WAIT_W
            while True:
                ready = yield conn.socket, wait
                if deadline and monotonic() > deadline:
                    raise e.ConnectionTimeout("connection timeout expired")
                if ready:
                    break

        elif status == POLL_OK:
            break
        elif status == POLL_FAILED:
            encoding = conninfo_encoding(conninfo)
            raise e.OperationalError(
                f"connection failed: {conn.get_error_message(encoding)}",
                pgconn=e.finish_pgconn(conn),
            )
        else:
            raise e.InternalError(
                f"unexpected poll status: {status}", pgconn=e.finish_pgconn(conn)
            )

    conn.nonblocking = 1
    return conn


def _cancel(cancel_conn: PGcancelConn, *, timeout: float = 0.0) -> PQGenConn[None]:
    deadline = monotonic() + timeout if timeout else 0.0
    while True:
        if deadline and monotonic() > deadline:
            raise e.CancellationTimeout("cancellation timeout expired")
        status = cancel_conn.poll()
        if status == POLL_OK:
            break
        elif status == POLL_READING:
            yield cancel_conn.socket, WAIT_R
        elif status == POLL_WRITING:
            yield cancel_conn.socket, WAIT_W
        elif status == POLL_FAILED:
            raise e.OperationalError(
                f"cancellation failed: {cancel_conn.get_error_message()}"
            )
        else:
            raise e.InternalError(f"unexpected poll status: {status}")


def _execute(pgconn: PGconn) -> PQGen[list[PGresult]]:
    """
    Generator sending a query and returning results without blocking.

    The query must have already been sent using `pgconn.send_query()` or
    similar. Flush the query and then return the result using nonblocking
    functions.

    Return the list of results returned by the database (whether success
    or error).
    """
    yield from _send(pgconn)
    rv = yield from _fetch_many(pgconn)
    return rv


def _send(pgconn: PGconn) -> PQGen[None]:
    """
    Generator to send a query to the server without blocking.

    The query must have already been sent using `pgconn.send_query()` or
    similar. Flush the query and then return the result using nonblocking
    functions.

    After this generator has finished you may want to cycle using `fetch()`
    to retrieve the results available.
    """
    while True:
        f = pgconn.flush()
        if f == 0:
            break

        while True:
            ready = yield WAIT_RW
            if ready:
                break

        if ready & READY_R:
            # This call may read notifies: they will be saved in the
            # PGconn buffer and passed to Python later, in `fetch()`.
            pgconn.consume_input()


def _fetch_many(pgconn: PGconn) -> PQGen[list[PGresult]]:
    """
    Generator retrieving results from the database without blocking.

    The query must have already been sent to the server, so pgconn.flush() has
    already returned 0.

    Return the list of results returned by the database (whether success
    or error).
    """
    results: list[PGresult] = []
    while True:
        try:
            res = yield from _fetch(pgconn)
        except e.DatabaseError:
            # What might have happened here is that a previuos error disconnected
            # the connection, for example a idle in transaction timeout.
            # Check if we had received an error before: if that's the case
            # just exit the loop. Our callers will handle this error and raise
            # it as an exception.
            if any(res.status == FATAL_ERROR for res in results):
                break
            else:
                raise

        if not res:
            break

        results.append(res)
        status = res.status
        if status == COPY_IN or status == COPY_OUT or status == COPY_BOTH:
            # After entering copy mode the libpq will create a phony result
            # for every request so let's break the endless loop.
            break

        if status == PIPELINE_SYNC:
            # PIPELINE_SYNC is not followed by a NULL, but we return it alone
            # similarly to other result sets.
            assert len(results) == 1, results
            break

    return results


def _fetch(pgconn: PGconn) -> PQGen[PGresult | None]:
    """
    Generator retrieving a single result from the database without blocking.

    The query must have already been sent to the server, so pgconn.flush() has
    already returned 0.

    Return a result from the database (whether success or error).
    """
    if pgconn.is_busy():
        while True:
            ready = yield WAIT_R
            if ready:
                break

        while True:
            pgconn.consume_input()
            if not pgconn.is_busy():
                break
            while True:
                ready = yield WAIT_R
                if ready:
                    break

    _consume_notifies(pgconn)

    return pgconn.get_result()


def _pipeline_communicate(
    pgconn: PGconn, commands: Deque[PipelineCommand]
) -> PQGen[list[list[PGresult]]]:
    """Generator to send queries from a connection in pipeline mode while also
    receiving results.

    Return a list results, including single PIPELINE_SYNC elements.
    """
    results = []

    while True:
        while True:
            ready = yield WAIT_RW
            if ready:
                break

        if ready & READY_R:
            pgconn.consume_input()
            _consume_notifies(pgconn)

            res: list[PGresult] = []
            while not pgconn.is_busy():
                r = pgconn.get_result()
                if r is None:
                    if not res:
                        break
                    results.append(res)
                    res = []
                else:
                    status = r.status
                    if status == PIPELINE_SYNC:
                        assert not res
                        results.append([r])
                    elif status == COPY_IN or status == COPY_OUT or status == COPY_BOTH:
                        # This shouldn't happen, but insisting hard enough, it will.
                        # For instance, in test_executemany_badquery(), with the COPY
                        # statement and the AsyncClientCursor, which disables
                        # prepared statements).
                        # Bail out from the resulting infinite loop.
                        raise e.NotSupportedError(
                            "COPY cannot be used in pipeline mode"
                        )
                    else:
                        res.append(r)

        if ready & READY_W:
            pgconn.flush()
            if not commands:
                break
            commands.popleft()()

    return results


def _consume_notifies(pgconn: PGconn) -> None:
    # Consume notifies
    while True:
        n = pgconn.notifies()
        if not n:
            break
        if pgconn.notify_handler:
            pgconn.notify_handler(n)


def notifies(pgconn: PGconn) -> PQGen[list[pq.PGnotify]]:
    yield WAIT_R
    pgconn.consume_input()

    ns = []
    while True:
        n = pgconn.notifies()
        if n:
            ns.append(n)
            if pgconn.notify_handler:
                pgconn.notify_handler(n)
        else:
            break

    return ns


def copy_from(pgconn: PGconn) -> PQGen[memoryview | PGresult]:
    while True:
        nbytes, data = pgconn.get_copy_data(1)
        if nbytes != 0:
            break

        # would block
        while True:
            ready = yield WAIT_R
            if ready:
                break
        pgconn.consume_input()

    if nbytes > 0:
        # some data
        return data

    # Retrieve the final result of copy
    results = yield from _fetch_many(pgconn)
    if len(results) > 1:
        # TODO: too brutal? Copy worked.
        raise e.ProgrammingError("you cannot mix COPY with other operations")
    result = results[0]
    if result.status != COMMAND_OK:
        raise e.error_from_result(result, encoding=pgconn._encoding)

    return result


def copy_to(pgconn: PGconn, buffer: Buffer, flush: bool = True) -> PQGen[None]:
    # Retry enqueuing data until successful.
    #
    # WARNING! This can cause an infinite loop if the buffer is too large. (see
    # ticket #255). We avoid it in the Copy object by splitting a large buffer
    # into smaller ones. We prefer to do it there instead of here in order to
    # do it upstream the queue decoupling the writer task from the producer one.
    while pgconn.put_copy_data(buffer) == 0:
        while True:
            ready = yield WAIT_W
            if ready:
                break

    # Flushing often has a good effect on macOS because memcpy operations
    # seem expensive on this platform so accumulating a large buffer has a
    # bad effect (see #745).
    if flush:
        # Repeat until it the message is flushed to the server
        while True:
            while True:
                ready = yield WAIT_W
                if ready:
                    break
            f = pgconn.flush()
            if f == 0:
                break


def copy_end(pgconn: PGconn, error: bytes | None) -> PQGen[PGresult]:
    # Retry enqueuing end copy message until successful
    while pgconn.put_copy_end(error) == 0:
        while True:
            ready = yield WAIT_W
            if ready:
                break

    # Repeat until it the message is flushed to the server
    while True:
        while True:
            ready = yield WAIT_W
            if ready:
                break
        f = pgconn.flush()
        if f == 0:
            break

    # Retrieve the final result of copy
    (result,) = yield from _fetch_many(pgconn)
    if result.status != COMMAND_OK:
        raise e.error_from_result(result, encoding=pgconn._encoding)

    return result


# Override functions with fast versions if available
if _psycopg:
    connect = _psycopg.connect
    cancel = _psycopg.cancel
    execute = _psycopg.execute
    send = _psycopg.send
    fetch_many = _psycopg.fetch_many
    fetch = _psycopg.fetch
    pipeline_communicate = _psycopg.pipeline_communicate

else:
    connect = _connect
    cancel = _cancel
    execute = _execute
    send = _send
    fetch_many = _fetch_many
    fetch = _fetch
    pipeline_communicate = _pipeline_communicate
