"""
libpq enum definitions for psycopg
"""

# Copyright (C) 2020 The Psycopg Team

from enum import IntEnum, IntFlag, auto

# Check in src/interfaces/libpq/libpq-fe.h for updates.


class ConnStatus(IntEnum):
    """
    Current status of the connection.
    """

    __module__ = "psycopg.pq"

    OK = 0
    """The connection is in a working state."""
    BAD = auto()
    """The connection is closed."""

    STARTED = auto()
    MADE = auto()
    AWAITING_RESPONSE = auto()
    AUTH_OK = auto()
    SETENV = auto()
    SSL_STARTUP = auto()
    NEEDED = auto()
    CHECK_WRITABLE = auto()
    CONSUME = auto()
    GSS_STARTUP = auto()
    CHECK_TARGET = auto()
    CHECK_STANDBY = auto()
    ALLOCATED = auto()  # Only for cancel connections.
    """Connection to the server hasn't been initiated yet."""


class PollingStatus(IntEnum):
    """
    The status of the socket during a connection.

    If ``READING`` or ``WRITING`` you may select before polling again.
    """

    __module__ = "psycopg.pq"

    FAILED = 0
    """Connection attempt failed."""
    READING = auto()
    """Will have to wait before reading new data."""
    WRITING = auto()
    """Will have to wait before writing new data."""
    OK = auto()
    """Connection completed."""

    ACTIVE = auto()


class ExecStatus(IntEnum):
    """
    The status of a command.
    """

    __module__ = "psycopg.pq"

    EMPTY_QUERY = 0
    """The string sent to the server was empty."""

    COMMAND_OK = auto()
    """Successful completion of a command returning no data."""

    TUPLES_OK = auto()
    """
    Successful completion of a command returning data (such as a SELECT or SHOW).
    """

    COPY_OUT = auto()
    """Copy Out (from server) data transfer started."""

    COPY_IN = auto()
    """Copy In (to server) data transfer started."""

    BAD_RESPONSE = auto()
    """The server's response was not understood."""

    NONFATAL_ERROR = auto()
    """A nonfatal error (a notice or warning) occurred."""

    FATAL_ERROR = auto()
    """A fatal error occurred."""

    COPY_BOTH = auto()
    """
    Copy In/Out (to and from server) data transfer started.

    This feature is currently used only for streaming replication, so this
    status should not occur in ordinary applications.
    """

    SINGLE_TUPLE = auto()
    """
    The PGresult contains a single result tuple from the current command.

    This status occurs only when single-row mode has been selected for the
    query.
    """

    PIPELINE_SYNC = auto()
    """
    The PGresult represents a synchronization point in pipeline mode,
    requested by PQpipelineSync.

    This status occurs only when pipeline mode has been selected.
    """

    PIPELINE_ABORTED = auto()
    """
    The PGresult represents a pipeline that has received an error from the server.

    PQgetResult must be called repeatedly, and each time it will return this
    status code until the end of the current pipeline, at which point it will
    return PGRES_PIPELINE_SYNC and normal processing can resume.
    """
    TUPLES_CHUNK = auto()
    """The PGresult contains several result tuples from the current command.

    This status occurs only when chunked mode has been selected for the query.
    """


class TransactionStatus(IntEnum):
    """
    The transaction status of a connection.
    """

    __module__ = "psycopg.pq"

    IDLE = 0
    """Connection ready, no transaction active."""

    ACTIVE = auto()
    """A command is in progress."""

    INTRANS = auto()
    """Connection idle in an open transaction."""

    INERROR = auto()
    """An error happened in the current transaction."""

    UNKNOWN = auto()
    """Unknown connection state, broken connection."""


class Ping(IntEnum):
    """Response from a ping attempt."""

    __module__ = "psycopg.pq"

    OK = 0
    """
    The server is running and appears to be accepting connections.
    """

    REJECT = auto()
    """
    The server is running but is in a state that disallows connections.
    """

    NO_RESPONSE = auto()
    """
    The server could not be contacted.
    """

    NO_ATTEMPT = auto()
    """
    No attempt was made to contact the server.
    """


class PipelineStatus(IntEnum):
    """Pipeline mode status of the libpq connection."""

    __module__ = "psycopg.pq"

    OFF = 0
    """
    The libpq connection is *not* in pipeline mode.
    """
    ON = auto()
    """
    The libpq connection is in pipeline mode.
    """
    ABORTED = auto()
    """
    The libpq connection is in pipeline mode and an error occurred while
    processing the current pipeline. The aborted flag is cleared when
    PQgetResult returns a result of type PGRES_PIPELINE_SYNC.
    """


class DiagnosticField(IntEnum):
    """
    Fields in an error report.
    """

    __module__ = "psycopg.pq"

    # from src/include/postgres_ext.h

    SEVERITY = ord("S")
    SEVERITY_NONLOCALIZED = ord("V")
    SQLSTATE = ord("C")
    MESSAGE_PRIMARY = ord("M")
    MESSAGE_DETAIL = ord("D")
    MESSAGE_HINT = ord("H")
    STATEMENT_POSITION = ord("P")
    INTERNAL_POSITION = ord("p")
    INTERNAL_QUERY = ord("q")
    CONTEXT = ord("W")
    SCHEMA_NAME = ord("s")
    TABLE_NAME = ord("t")
    COLUMN_NAME = ord("c")
    DATATYPE_NAME = ord("d")
    CONSTRAINT_NAME = ord("n")
    SOURCE_FILE = ord("F")
    SOURCE_LINE = ord("L")
    SOURCE_FUNCTION = ord("R")


class Format(IntEnum):
    """
    Enum representing the format of a query argument or return value.

    These values are only the ones managed by the libpq. `~psycopg` may also
    support automatically-chosen values: see `psycopg.adapt.PyFormat`.
    """

    __module__ = "psycopg.pq"

    TEXT = 0
    """Text parameter."""
    BINARY = 1
    """Binary parameter."""


class Trace(IntFlag):
    """
    Enum to control tracing of the client/server communication.
    """

    __module__ = "psycopg.pq"

    SUPPRESS_TIMESTAMPS = 1
    """Do not include timestamps in messages."""

    REGRESS_MODE = 2
    """Redact some fields, e.g. OIDs, from messages."""
