"""
psycopg exceptions

DBAPI-defined Exceptions are defined in the following hierarchy::

    Exceptions
    |__Warning
    |__Error
       |__InterfaceError
       |__DatabaseError
          |__DataError
          |__OperationalError
          |__IntegrityError
          |__InternalError
          |__ProgrammingError
          |__NotSupportedError
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, NoReturn, Sequence
from asyncio import CancelledError
from dataclasses import dataclass, field, fields

from .pq.abc import PGconn, PGresult
from ._compat import TypeAlias, TypeGuard
from .pq._enums import ConnStatus, DiagnosticField, PipelineStatus, TransactionStatus

if TYPE_CHECKING:
    from .pq.misc import ConninfoOption, PGnotify

ErrorInfo: TypeAlias = "PGresult | dict[int, bytes | None] | None"

_sqlcodes: dict[str, type[Error]] = {}


@dataclass
class FinishedPGconn:
    """Finished libpq connection.

    Attributes are set from a real `~psycopg.pq.PGconn` but any operations will
    raise an `~psycopg.OperationalError`.
    """

    info: list[ConninfoOption] = field(default_factory=list)

    db: bytes = b""
    user: bytes = b""
    password: bytes = b""
    host: bytes = b""
    hostaddr: bytes = b""
    port: bytes = b""
    tty: bytes = b""
    options: bytes = b""
    status: int = ConnStatus.BAD.value
    transaction_status: int = TransactionStatus.UNKNOWN.value
    pipeline_status: int = PipelineStatus.OFF.value

    error_message: bytes = b""
    _encoding: str = "utf-8"
    server_version: int = 0

    backend_pid: int = 0
    needs_password: bool = False
    used_password: bool = False
    ssl_in_use: bool = False

    nonblocking: int = 0

    notice_handler: Callable[[PGresult], None] | None = None
    notify_handler: Callable[[PGnotify], None] | None = None

    @staticmethod
    def _raise() -> NoReturn:
        raise OperationalError("the connection is closed")

    @classmethod
    def connect(cls, *args: Any) -> NoReturn:
        raise TypeError(f"{cls} is unusable")

    @classmethod
    def connect_start(cls, *args: Any) -> NoReturn:
        raise TypeError(f"{cls} is unusable")

    def connect_poll(self) -> NoReturn:
        self._raise()

    def finish(self) -> None:
        pass

    def reset(self) -> NoReturn:
        self._raise()

    def get_error_message(self, encoding: str = "") -> str:
        return "the connection is closed"

    def reset_start(self) -> NoReturn:
        self._raise()

    def reset_poll(self) -> NoReturn:
        self._raise()

    @classmethod
    def ping(cls, *args: Any) -> NoReturn:
        raise TypeError(f"{cls} is unusable")

    def parameter_status(self, *args: Any) -> NoReturn:
        self._raise()

    @property
    def socket(self) -> NoReturn:
        self._raise()

    def exec_(self, *args: Any) -> NoReturn:
        self._raise()

    def send_query(self, *args: Any) -> None:
        self._raise()

    def exec_params(self, *args: Any) -> NoReturn:
        self._raise()

    def send_query_params(self, *args: Any) -> NoReturn:
        self._raise()

    def send_prepare(self, *args: Any) -> NoReturn:
        self._raise()

    def send_query_prepared(self, *args: Any) -> NoReturn:
        self._raise()

    def prepare(self, *args: Any) -> NoReturn:
        self._raise()

    def exec_prepared(self, *args: Any) -> NoReturn:
        self._raise()

    def describe_prepared(self, *args: Any) -> NoReturn:
        self._raise()

    def send_describe_prepared(self, *args: Any) -> NoReturn:
        self._raise()

    def describe_portal(self, *args: Any) -> NoReturn:
        self._raise()

    def send_describe_portal(self, *args: Any) -> NoReturn:
        self._raise()

    def close_prepared(self, *args: Any) -> NoReturn:
        self._raise()

    def send_close_prepared(self, *args: Any) -> NoReturn:
        self._raise()

    def close_portal(self, *args: Any) -> NoReturn:
        self._raise()

    def send_close_portal(self, *args: Any) -> NoReturn:
        self._raise()

    def get_result(self) -> NoReturn:
        self._raise()

    def consume_input(self) -> NoReturn:
        self._raise()

    def is_busy(self) -> NoReturn:
        self._raise()

    def flush(self) -> NoReturn:
        self._raise()

    def set_single_row_mode(self) -> NoReturn:
        self._raise()

    def set_chunked_rows_mode(self, size: int) -> NoReturn:
        self._raise()

    def cancel_conn(self) -> NoReturn:
        self._raise()

    def get_cancel(self) -> NoReturn:
        self._raise()

    def notifies(self) -> NoReturn:
        self._raise()

    def put_copy_data(self, *args: Any) -> NoReturn:
        self._raise()

    def put_copy_end(self, *args: Any) -> NoReturn:
        self._raise()

    def get_copy_data(self, *args: Any) -> NoReturn:
        self._raise()

    def trace(self, *args: Any) -> NoReturn:
        self._raise()

    def set_trace_flags(self, *args: Any) -> NoReturn:
        self._raise()

    def untrace(self) -> NoReturn:
        self._raise()

    def encrypt_password(self, *args: Any) -> NoReturn:
        self._raise()

    def change_password(self, *args: Any) -> NoReturn:
        self._raise()

    def make_empty_result(self, *args: Any) -> NoReturn:
        self._raise()

    def enter_pipeline_mode(self) -> NoReturn:
        self._raise()

    def exit_pipeline_mode(self) -> NoReturn:
        self._raise()

    def pipeline_sync(self) -> NoReturn:
        self._raise()

    def send_flush_request(self) -> NoReturn:
        self._raise()


def finish_pgconn(pgconn: PGconn) -> PGconn:
    args = {}
    for f in fields(FinishedPGconn):
        try:
            args[f.name] = getattr(pgconn, f.name)
        except Exception:
            pass
    pgconn.finish()
    return FinishedPGconn(**args)


class Warning(Exception):
    """
    Exception raised for important warnings.

    Defined for DBAPI compatibility, but never raised by ``psycopg``.
    """

    __module__ = "psycopg"


class Error(Exception):
    """
    Base exception for all the errors psycopg will raise.

    Exception that is the base class of all other error exceptions. You can
    use this to catch all errors with one single `!except` statement.

    This exception is guaranteed to be picklable.
    """

    __module__ = "psycopg"

    sqlstate: str | None = None

    def __init__(
        self,
        *args: Sequence[Any],
        info: ErrorInfo = None,
        encoding: str = "utf-8",
        pgconn: PGconn | None = None,
    ):
        super().__init__(*args)
        self._info = info
        self._encoding = encoding
        self._pgconn = pgconn

        # Handle sqlstate codes for which we don't have a class.
        if not self.sqlstate and info:
            self.sqlstate = self.diag.sqlstate

    @property
    def pgconn(self) -> PGconn | None:
        """The connection object, if the error was raised from a connection attempt.

        :rtype: psycopg.pq.PGconn | None
        """
        return self._pgconn if self._pgconn else None

    @property
    def pgresult(self) -> PGresult | None:
        """The result object, if the exception was raised after a failed query.

        :rtype: psycopg.pq.PGresult | None
        """
        return self._info if _is_pgresult(self._info) else None

    @property
    def diag(self) -> Diagnostic:
        """
        A `Diagnostic` object to inspect details of the errors from the database.
        """
        return Diagnostic(self._info, encoding=self._encoding)

    def __reduce__(self) -> str | tuple[Any, ...]:
        res = super().__reduce__()
        if isinstance(res, tuple) and len(res) >= 3:
            # To make the exception picklable
            res[2]["_info"] = _info_to_dict(self._info)
            res[2]["_pgconn"] = None

        return res


class InterfaceError(Error):
    """
    An error related to the database interface rather than the database itself.
    """

    __module__ = "psycopg"


class DatabaseError(Error):
    """
    Exception raised for errors that are related to the database.
    """

    __module__ = "psycopg"

    def __init_subclass__(cls, code: str | None = None, name: str | None = None):
        if code:
            _sqlcodes[code] = cls
            cls.sqlstate = code
        if name:
            _sqlcodes[name] = cls


class DataError(DatabaseError):
    """
    An error caused by problems with the processed data.

    Examples may be division by zero, numeric value out of range, etc.
    """

    __module__ = "psycopg"


class OperationalError(DatabaseError):
    """
    An error related to the database's operation.

    These errors are not necessarily under the control of the programmer, e.g.
    an unexpected disconnect occurs, the data source name is not found, a
    transaction could not be processed, a memory allocation error occurred
    during processing, etc.
    """

    __module__ = "psycopg"


class IntegrityError(DatabaseError):
    """
    An error caused when the relational integrity of the database is affected.

    An example may be a foreign key check failed.
    """

    __module__ = "psycopg"


class InternalError(DatabaseError):
    """
    An error generated when the database encounters an internal error,

    Examples could be the cursor is not valid anymore, the transaction is out
    of sync, etc.
    """

    __module__ = "psycopg"


class ProgrammingError(DatabaseError):
    """
    Exception raised for programming errors

    Examples may be table not found or already exists, syntax error in the SQL
    statement, wrong number of parameters specified, etc.
    """

    __module__ = "psycopg"


class NotSupportedError(DatabaseError):
    """
    A method or database API was used which is not supported by the database.
    """

    __module__ = "psycopg"


class ConnectionTimeout(OperationalError):
    """
    Exception raised on timeout of the `~psycopg.Connection.connect()` method.

    The error is raised if the ``connect_timeout`` is specified and a
    connection is not obtained in useful time.

    Subclass of `~psycopg.OperationalError`.
    """


class CancellationTimeout(OperationalError):
    """
    Exception raised on timeout of connection's
    `~psycopg.Connection.cancel_safe()` method.

    Subclass of `~psycopg.OperationalError`.
    """


class PipelineAborted(OperationalError):
    """
    Raised when a operation fails because the current pipeline is in aborted state.

    Subclass of `~psycopg.OperationalError`.
    """


class Diagnostic:
    """Details from a database error report."""

    def __init__(self, info: ErrorInfo, encoding: str = "utf-8"):
        self._info = info
        self._encoding = encoding

    @property
    def severity(self) -> str | None:
        return self._error_message(DiagnosticField.SEVERITY)

    @property
    def severity_nonlocalized(self) -> str | None:
        return self._error_message(DiagnosticField.SEVERITY_NONLOCALIZED)

    @property
    def sqlstate(self) -> str | None:
        return self._error_message(DiagnosticField.SQLSTATE)

    @property
    def message_primary(self) -> str | None:
        return self._error_message(DiagnosticField.MESSAGE_PRIMARY)

    @property
    def message_detail(self) -> str | None:
        return self._error_message(DiagnosticField.MESSAGE_DETAIL)

    @property
    def message_hint(self) -> str | None:
        return self._error_message(DiagnosticField.MESSAGE_HINT)

    @property
    def statement_position(self) -> str | None:
        return self._error_message(DiagnosticField.STATEMENT_POSITION)

    @property
    def internal_position(self) -> str | None:
        return self._error_message(DiagnosticField.INTERNAL_POSITION)

    @property
    def internal_query(self) -> str | None:
        return self._error_message(DiagnosticField.INTERNAL_QUERY)

    @property
    def context(self) -> str | None:
        return self._error_message(DiagnosticField.CONTEXT)

    @property
    def schema_name(self) -> str | None:
        return self._error_message(DiagnosticField.SCHEMA_NAME)

    @property
    def table_name(self) -> str | None:
        return self._error_message(DiagnosticField.TABLE_NAME)

    @property
    def column_name(self) -> str | None:
        return self._error_message(DiagnosticField.COLUMN_NAME)

    @property
    def datatype_name(self) -> str | None:
        return self._error_message(DiagnosticField.DATATYPE_NAME)

    @property
    def constraint_name(self) -> str | None:
        return self._error_message(DiagnosticField.CONSTRAINT_NAME)

    @property
    def source_file(self) -> str | None:
        return self._error_message(DiagnosticField.SOURCE_FILE)

    @property
    def source_line(self) -> str | None:
        return self._error_message(DiagnosticField.SOURCE_LINE)

    @property
    def source_function(self) -> str | None:
        return self._error_message(DiagnosticField.SOURCE_FUNCTION)

    def _error_message(self, field: DiagnosticField) -> str | None:
        if self._info:
            if isinstance(self._info, dict):
                val = self._info.get(field)
            else:
                val = self._info.error_field(field)

            if val is not None:
                return val.decode(self._encoding, "replace")

        return None

    def __reduce__(self) -> str | tuple[Any, ...]:
        res = super().__reduce__()
        if isinstance(res, tuple) and len(res) >= 3:
            res[2]["_info"] = _info_to_dict(self._info)

        return res


def _info_to_dict(info: ErrorInfo) -> ErrorInfo:
    """
    Convert a PGresult to a dictionary to make the info picklable.
    """
    # PGresult is a protocol, can't use isinstance
    if _is_pgresult(info):
        return {v: info.error_field(v) for v in DiagnosticField}
    else:
        return info


def lookup(sqlstate: str) -> type[Error]:
    """Lookup an error code or `constant name`__ and return its exception class.

    Raise `!KeyError` if the code is not found.

    .. __: https://www.postgresql.org/docs/current/errcodes-appendix.html
            #ERRCODES-TABLE
    """
    return _sqlcodes[sqlstate.upper()]


def error_from_result(result: PGresult, encoding: str = "utf-8") -> Error:
    state = result.error_field(DiagnosticField.SQLSTATE) or b""
    cls = _class_for_state(state.decode("utf-8", "replace"))
    return cls(result.get_error_message(encoding), info=result, encoding=encoding)


def _is_pgresult(info: ErrorInfo) -> TypeGuard[PGresult]:
    """Return True if an ErrorInfo is a PGresult instance."""
    # PGresult is a protocol, can't use isinstance
    return hasattr(info, "error_field")


def _class_for_state(sqlstate: str) -> type[Error]:
    try:
        return lookup(sqlstate)
    except KeyError:
        return get_base_exception(sqlstate)


def get_base_exception(sqlstate: str) -> type[Error]:
    return (
        _base_exc_map.get(sqlstate[:2])
        or _base_exc_map.get(sqlstate[:1])
        or DatabaseError
    )


_base_exc_map = {
    "08": OperationalError,  # Connection Exception
    "0A": NotSupportedError,  # Feature Not Supported
    "20": ProgrammingError,  # Case Not Foud
    "21": ProgrammingError,  # Cardinality Violation
    "22": DataError,  # Data Exception
    "23": IntegrityError,  # Integrity Constraint Violation
    "24": InternalError,  # Invalid Cursor State
    "25": InternalError,  # Invalid Transaction State
    "26": ProgrammingError,  # Invalid SQL Statement Name *
    "27": OperationalError,  # Triggered Data Change Violation
    "28": OperationalError,  # Invalid Authorization Specification
    "2B": InternalError,  # Dependent Privilege Descriptors Still Exist
    "2D": InternalError,  # Invalid Transaction Termination
    "2F": OperationalError,  # SQL Routine Exception *
    "34": ProgrammingError,  # Invalid Cursor Name *
    "38": OperationalError,  # External Routine Exception *
    "39": OperationalError,  # External Routine Invocation Exception *
    "3B": OperationalError,  # Savepoint Exception *
    "3D": ProgrammingError,  # Invalid Catalog Name
    "3F": ProgrammingError,  # Invalid Schema Name
    "40": OperationalError,  # Transaction Rollback
    "42": ProgrammingError,  # Syntax Error or Access Rule Violation
    "44": ProgrammingError,  # WITH CHECK OPTION Violation
    "53": OperationalError,  # Insufficient Resources
    "54": OperationalError,  # Program Limit Exceeded
    "55": OperationalError,  # Object Not In Prerequisite State
    "57": OperationalError,  # Operator Intervention
    "58": OperationalError,  # System Error (errors external to PostgreSQL itself)
    "F": OperationalError,  # Configuration File Error
    "H": OperationalError,  # Foreign Data Wrapper Error (SQL/MED)
    "P": ProgrammingError,  # PL/pgSQL Error
    "X": InternalError,  # Internal Error
}


# Error classes generated by tools/update_errors.py

# fmt: off
# autogenerated: start


# Class 02 - No Data (this is also a warning class per the SQL standard)

class NoData(DatabaseError,
    code='02000', name='NO_DATA'):
    pass

class NoAdditionalDynamicResultSetsReturned(DatabaseError,
    code='02001', name='NO_ADDITIONAL_DYNAMIC_RESULT_SETS_RETURNED'):
    pass


# Class 03 - SQL Statement Not Yet Complete

class SqlStatementNotYetComplete(DatabaseError,
    code='03000', name='SQL_STATEMENT_NOT_YET_COMPLETE'):
    pass


# Class 08 - Connection Exception

class ConnectionException(OperationalError,
    code='08000', name='CONNECTION_EXCEPTION'):
    pass

class SqlclientUnableToEstablishSqlconnection(OperationalError,
    code='08001', name='SQLCLIENT_UNABLE_TO_ESTABLISH_SQLCONNECTION'):
    pass

class ConnectionDoesNotExist(OperationalError,
    code='08003', name='CONNECTION_DOES_NOT_EXIST'):
    pass

class SqlserverRejectedEstablishmentOfSqlconnection(OperationalError,
    code='08004', name='SQLSERVER_REJECTED_ESTABLISHMENT_OF_SQLCONNECTION'):
    pass

class ConnectionFailure(OperationalError,
    code='08006', name='CONNECTION_FAILURE'):
    pass

class TransactionResolutionUnknown(OperationalError,
    code='08007', name='TRANSACTION_RESOLUTION_UNKNOWN'):
    pass

class ProtocolViolation(OperationalError,
    code='08P01', name='PROTOCOL_VIOLATION'):
    pass


# Class 09 - Triggered Action Exception

class TriggeredActionException(DatabaseError,
    code='09000', name='TRIGGERED_ACTION_EXCEPTION'):
    pass


# Class 0A - Feature Not Supported

class FeatureNotSupported(NotSupportedError,
    code='0A000', name='FEATURE_NOT_SUPPORTED'):
    pass


# Class 0B - Invalid Transaction Initiation

class InvalidTransactionInitiation(DatabaseError,
    code='0B000', name='INVALID_TRANSACTION_INITIATION'):
    pass


# Class 0F - Locator Exception

class LocatorException(DatabaseError,
    code='0F000', name='LOCATOR_EXCEPTION'):
    pass

class InvalidLocatorSpecification(DatabaseError,
    code='0F001', name='INVALID_LOCATOR_SPECIFICATION'):
    pass


# Class 0L - Invalid Grantor

class InvalidGrantor(DatabaseError,
    code='0L000', name='INVALID_GRANTOR'):
    pass

class InvalidGrantOperation(DatabaseError,
    code='0LP01', name='INVALID_GRANT_OPERATION'):
    pass


# Class 0P - Invalid Role Specification

class InvalidRoleSpecification(DatabaseError,
    code='0P000', name='INVALID_ROLE_SPECIFICATION'):
    pass


# Class 0Z - Diagnostics Exception

class DiagnosticsException(DatabaseError,
    code='0Z000', name='DIAGNOSTICS_EXCEPTION'):
    pass

class StackedDiagnosticsAccessedWithoutActiveHandler(DatabaseError,
    code='0Z002', name='STACKED_DIAGNOSTICS_ACCESSED_WITHOUT_ACTIVE_HANDLER'):
    pass


# Class 20 - Case Not Found

class CaseNotFound(ProgrammingError,
    code='20000', name='CASE_NOT_FOUND'):
    pass


# Class 21 - Cardinality Violation

class CardinalityViolation(ProgrammingError,
    code='21000', name='CARDINALITY_VIOLATION'):
    pass


# Class 22 - Data Exception

class DataException(DataError,
    code='22000', name='DATA_EXCEPTION'):
    pass

class StringDataRightTruncation(DataError,
    code='22001', name='STRING_DATA_RIGHT_TRUNCATION'):
    pass

class NullValueNoIndicatorParameter(DataError,
    code='22002', name='NULL_VALUE_NO_INDICATOR_PARAMETER'):
    pass

class NumericValueOutOfRange(DataError,
    code='22003', name='NUMERIC_VALUE_OUT_OF_RANGE'):
    pass

class NullValueNotAllowed(DataError,
    code='22004', name='NULL_VALUE_NOT_ALLOWED'):
    pass

class ErrorInAssignment(DataError,
    code='22005', name='ERROR_IN_ASSIGNMENT'):
    pass

class InvalidDatetimeFormat(DataError,
    code='22007', name='INVALID_DATETIME_FORMAT'):
    pass

class DatetimeFieldOverflow(DataError,
    code='22008', name='DATETIME_FIELD_OVERFLOW'):
    pass

class InvalidTimeZoneDisplacementValue(DataError,
    code='22009', name='INVALID_TIME_ZONE_DISPLACEMENT_VALUE'):
    pass

class EscapeCharacterConflict(DataError,
    code='2200B', name='ESCAPE_CHARACTER_CONFLICT'):
    pass

class InvalidUseOfEscapeCharacter(DataError,
    code='2200C', name='INVALID_USE_OF_ESCAPE_CHARACTER'):
    pass

class InvalidEscapeOctet(DataError,
    code='2200D', name='INVALID_ESCAPE_OCTET'):
    pass

class ZeroLengthCharacterString(DataError,
    code='2200F', name='ZERO_LENGTH_CHARACTER_STRING'):
    pass

class MostSpecificTypeMismatch(DataError,
    code='2200G', name='MOST_SPECIFIC_TYPE_MISMATCH'):
    pass

class SequenceGeneratorLimitExceeded(DataError,
    code='2200H', name='SEQUENCE_GENERATOR_LIMIT_EXCEEDED'):
    pass

class NotAnXmlDocument(DataError,
    code='2200L', name='NOT_AN_XML_DOCUMENT'):
    pass

class InvalidXmlDocument(DataError,
    code='2200M', name='INVALID_XML_DOCUMENT'):
    pass

class InvalidXmlContent(DataError,
    code='2200N', name='INVALID_XML_CONTENT'):
    pass

class InvalidXmlComment(DataError,
    code='2200S', name='INVALID_XML_COMMENT'):
    pass

class InvalidXmlProcessingInstruction(DataError,
    code='2200T', name='INVALID_XML_PROCESSING_INSTRUCTION'):
    pass

class InvalidIndicatorParameterValue(DataError,
    code='22010', name='INVALID_INDICATOR_PARAMETER_VALUE'):
    pass

class SubstringError(DataError,
    code='22011', name='SUBSTRING_ERROR'):
    pass

class DivisionByZero(DataError,
    code='22012', name='DIVISION_BY_ZERO'):
    pass

class InvalidPrecedingOrFollowingSize(DataError,
    code='22013', name='INVALID_PRECEDING_OR_FOLLOWING_SIZE'):
    pass

class InvalidArgumentForNtileFunction(DataError,
    code='22014', name='INVALID_ARGUMENT_FOR_NTILE_FUNCTION'):
    pass

class IntervalFieldOverflow(DataError,
    code='22015', name='INTERVAL_FIELD_OVERFLOW'):
    pass

class InvalidArgumentForNthValueFunction(DataError,
    code='22016', name='INVALID_ARGUMENT_FOR_NTH_VALUE_FUNCTION'):
    pass

class InvalidCharacterValueForCast(DataError,
    code='22018', name='INVALID_CHARACTER_VALUE_FOR_CAST'):
    pass

class InvalidEscapeCharacter(DataError,
    code='22019', name='INVALID_ESCAPE_CHARACTER'):
    pass

class InvalidRegularExpression(DataError,
    code='2201B', name='INVALID_REGULAR_EXPRESSION'):
    pass

class InvalidArgumentForLogarithm(DataError,
    code='2201E', name='INVALID_ARGUMENT_FOR_LOGARITHM'):
    pass

class InvalidArgumentForPowerFunction(DataError,
    code='2201F', name='INVALID_ARGUMENT_FOR_POWER_FUNCTION'):
    pass

class InvalidArgumentForWidthBucketFunction(DataError,
    code='2201G', name='INVALID_ARGUMENT_FOR_WIDTH_BUCKET_FUNCTION'):
    pass

class InvalidRowCountInLimitClause(DataError,
    code='2201W', name='INVALID_ROW_COUNT_IN_LIMIT_CLAUSE'):
    pass

class InvalidRowCountInResultOffsetClause(DataError,
    code='2201X', name='INVALID_ROW_COUNT_IN_RESULT_OFFSET_CLAUSE'):
    pass

class CharacterNotInRepertoire(DataError,
    code='22021', name='CHARACTER_NOT_IN_REPERTOIRE'):
    pass

class IndicatorOverflow(DataError,
    code='22022', name='INDICATOR_OVERFLOW'):
    pass

class InvalidParameterValue(DataError,
    code='22023', name='INVALID_PARAMETER_VALUE'):
    pass

class UnterminatedCString(DataError,
    code='22024', name='UNTERMINATED_C_STRING'):
    pass

class InvalidEscapeSequence(DataError,
    code='22025', name='INVALID_ESCAPE_SEQUENCE'):
    pass

class StringDataLengthMismatch(DataError,
    code='22026', name='STRING_DATA_LENGTH_MISMATCH'):
    pass

class TrimError(DataError,
    code='22027', name='TRIM_ERROR'):
    pass

class ArraySubscriptError(DataError,
    code='2202E', name='ARRAY_SUBSCRIPT_ERROR'):
    pass

class InvalidTablesampleRepeat(DataError,
    code='2202G', name='INVALID_TABLESAMPLE_REPEAT'):
    pass

class InvalidTablesampleArgument(DataError,
    code='2202H', name='INVALID_TABLESAMPLE_ARGUMENT'):
    pass

class DuplicateJsonObjectKeyValue(DataError,
    code='22030', name='DUPLICATE_JSON_OBJECT_KEY_VALUE'):
    pass

class InvalidArgumentForSqlJsonDatetimeFunction(DataError,
    code='22031', name='INVALID_ARGUMENT_FOR_SQL_JSON_DATETIME_FUNCTION'):
    pass

class InvalidJsonText(DataError,
    code='22032', name='INVALID_JSON_TEXT'):
    pass

class InvalidSqlJsonSubscript(DataError,
    code='22033', name='INVALID_SQL_JSON_SUBSCRIPT'):
    pass

class MoreThanOneSqlJsonItem(DataError,
    code='22034', name='MORE_THAN_ONE_SQL_JSON_ITEM'):
    pass

class NoSqlJsonItem(DataError,
    code='22035', name='NO_SQL_JSON_ITEM'):
    pass

class NonNumericSqlJsonItem(DataError,
    code='22036', name='NON_NUMERIC_SQL_JSON_ITEM'):
    pass

class NonUniqueKeysInAJsonObject(DataError,
    code='22037', name='NON_UNIQUE_KEYS_IN_A_JSON_OBJECT'):
    pass

class SingletonSqlJsonItemRequired(DataError,
    code='22038', name='SINGLETON_SQL_JSON_ITEM_REQUIRED'):
    pass

class SqlJsonArrayNotFound(DataError,
    code='22039', name='SQL_JSON_ARRAY_NOT_FOUND'):
    pass

class SqlJsonMemberNotFound(DataError,
    code='2203A', name='SQL_JSON_MEMBER_NOT_FOUND'):
    pass

class SqlJsonNumberNotFound(DataError,
    code='2203B', name='SQL_JSON_NUMBER_NOT_FOUND'):
    pass

class SqlJsonObjectNotFound(DataError,
    code='2203C', name='SQL_JSON_OBJECT_NOT_FOUND'):
    pass

class TooManyJsonArrayElements(DataError,
    code='2203D', name='TOO_MANY_JSON_ARRAY_ELEMENTS'):
    pass

class TooManyJsonObjectMembers(DataError,
    code='2203E', name='TOO_MANY_JSON_OBJECT_MEMBERS'):
    pass

class SqlJsonScalarRequired(DataError,
    code='2203F', name='SQL_JSON_SCALAR_REQUIRED'):
    pass

class SqlJsonItemCannotBeCastToTargetType(DataError,
    code='2203G', name='SQL_JSON_ITEM_CANNOT_BE_CAST_TO_TARGET_TYPE'):
    pass

class FloatingPointException(DataError,
    code='22P01', name='FLOATING_POINT_EXCEPTION'):
    pass

class InvalidTextRepresentation(DataError,
    code='22P02', name='INVALID_TEXT_REPRESENTATION'):
    pass

class InvalidBinaryRepresentation(DataError,
    code='22P03', name='INVALID_BINARY_REPRESENTATION'):
    pass

class BadCopyFileFormat(DataError,
    code='22P04', name='BAD_COPY_FILE_FORMAT'):
    pass

class UntranslatableCharacter(DataError,
    code='22P05', name='UNTRANSLATABLE_CHARACTER'):
    pass

class NonstandardUseOfEscapeCharacter(DataError,
    code='22P06', name='NONSTANDARD_USE_OF_ESCAPE_CHARACTER'):
    pass


# Class 23 - Integrity Constraint Violation

class IntegrityConstraintViolation(IntegrityError,
    code='23000', name='INTEGRITY_CONSTRAINT_VIOLATION'):
    pass

class RestrictViolation(IntegrityError,
    code='23001', name='RESTRICT_VIOLATION'):
    pass

class NotNullViolation(IntegrityError,
    code='23502', name='NOT_NULL_VIOLATION'):
    pass

class ForeignKeyViolation(IntegrityError,
    code='23503', name='FOREIGN_KEY_VIOLATION'):
    pass

class UniqueViolation(IntegrityError,
    code='23505', name='UNIQUE_VIOLATION'):
    pass

class CheckViolation(IntegrityError,
    code='23514', name='CHECK_VIOLATION'):
    pass

class ExclusionViolation(IntegrityError,
    code='23P01', name='EXCLUSION_VIOLATION'):
    pass


# Class 24 - Invalid Cursor State

class InvalidCursorState(InternalError,
    code='24000', name='INVALID_CURSOR_STATE'):
    pass


# Class 25 - Invalid Transaction State

class InvalidTransactionState(InternalError,
    code='25000', name='INVALID_TRANSACTION_STATE'):
    pass

class ActiveSqlTransaction(InternalError,
    code='25001', name='ACTIVE_SQL_TRANSACTION'):
    pass

class BranchTransactionAlreadyActive(InternalError,
    code='25002', name='BRANCH_TRANSACTION_ALREADY_ACTIVE'):
    pass

class InappropriateAccessModeForBranchTransaction(InternalError,
    code='25003', name='INAPPROPRIATE_ACCESS_MODE_FOR_BRANCH_TRANSACTION'):
    pass

class InappropriateIsolationLevelForBranchTransaction(InternalError,
    code='25004', name='INAPPROPRIATE_ISOLATION_LEVEL_FOR_BRANCH_TRANSACTION'):
    pass

class NoActiveSqlTransactionForBranchTransaction(InternalError,
    code='25005', name='NO_ACTIVE_SQL_TRANSACTION_FOR_BRANCH_TRANSACTION'):
    pass

class ReadOnlySqlTransaction(InternalError,
    code='25006', name='READ_ONLY_SQL_TRANSACTION'):
    pass

class SchemaAndDataStatementMixingNotSupported(InternalError,
    code='25007', name='SCHEMA_AND_DATA_STATEMENT_MIXING_NOT_SUPPORTED'):
    pass

class HeldCursorRequiresSameIsolationLevel(InternalError,
    code='25008', name='HELD_CURSOR_REQUIRES_SAME_ISOLATION_LEVEL'):
    pass

class NoActiveSqlTransaction(InternalError,
    code='25P01', name='NO_ACTIVE_SQL_TRANSACTION'):
    pass

class InFailedSqlTransaction(InternalError,
    code='25P02', name='IN_FAILED_SQL_TRANSACTION'):
    pass

class IdleInTransactionSessionTimeout(InternalError,
    code='25P03', name='IDLE_IN_TRANSACTION_SESSION_TIMEOUT'):
    pass

class TransactionTimeout(InternalError,
    code='25P04', name='TRANSACTION_TIMEOUT'):
    pass


# Class 26 - Invalid SQL Statement Name

class InvalidSqlStatementName(ProgrammingError,
    code='26000', name='INVALID_SQL_STATEMENT_NAME'):
    pass


# Class 27 - Triggered Data Change Violation

class TriggeredDataChangeViolation(OperationalError,
    code='27000', name='TRIGGERED_DATA_CHANGE_VIOLATION'):
    pass


# Class 28 - Invalid Authorization Specification

class InvalidAuthorizationSpecification(OperationalError,
    code='28000', name='INVALID_AUTHORIZATION_SPECIFICATION'):
    pass

class InvalidPassword(OperationalError,
    code='28P01', name='INVALID_PASSWORD'):
    pass


# Class 2B - Dependent Privilege Descriptors Still Exist

class DependentPrivilegeDescriptorsStillExist(InternalError,
    code='2B000', name='DEPENDENT_PRIVILEGE_DESCRIPTORS_STILL_EXIST'):
    pass

class DependentObjectsStillExist(InternalError,
    code='2BP01', name='DEPENDENT_OBJECTS_STILL_EXIST'):
    pass


# Class 2D - Invalid Transaction Termination

class InvalidTransactionTermination(InternalError,
    code='2D000', name='INVALID_TRANSACTION_TERMINATION'):
    pass


# Class 2F - SQL Routine Exception

class SqlRoutineException(OperationalError,
    code='2F000', name='SQL_ROUTINE_EXCEPTION'):
    pass

class ModifyingSqlDataNotPermitted(OperationalError,
    code='2F002', name='MODIFYING_SQL_DATA_NOT_PERMITTED'):
    pass

class ProhibitedSqlStatementAttempted(OperationalError,
    code='2F003', name='PROHIBITED_SQL_STATEMENT_ATTEMPTED'):
    pass

class ReadingSqlDataNotPermitted(OperationalError,
    code='2F004', name='READING_SQL_DATA_NOT_PERMITTED'):
    pass

class FunctionExecutedNoReturnStatement(OperationalError,
    code='2F005', name='FUNCTION_EXECUTED_NO_RETURN_STATEMENT'):
    pass


# Class 34 - Invalid Cursor Name

class InvalidCursorName(ProgrammingError,
    code='34000', name='INVALID_CURSOR_NAME'):
    pass


# Class 38 - External Routine Exception

class ExternalRoutineException(OperationalError,
    code='38000', name='EXTERNAL_ROUTINE_EXCEPTION'):
    pass

class ContainingSqlNotPermitted(OperationalError,
    code='38001', name='CONTAINING_SQL_NOT_PERMITTED'):
    pass

class ModifyingSqlDataNotPermittedExt(OperationalError,
    code='38002', name='MODIFYING_SQL_DATA_NOT_PERMITTED'):
    pass

class ProhibitedSqlStatementAttemptedExt(OperationalError,
    code='38003', name='PROHIBITED_SQL_STATEMENT_ATTEMPTED'):
    pass

class ReadingSqlDataNotPermittedExt(OperationalError,
    code='38004', name='READING_SQL_DATA_NOT_PERMITTED'):
    pass


# Class 39 - External Routine Invocation Exception

class ExternalRoutineInvocationException(OperationalError,
    code='39000', name='EXTERNAL_ROUTINE_INVOCATION_EXCEPTION'):
    pass

class InvalidSqlstateReturned(OperationalError,
    code='39001', name='INVALID_SQLSTATE_RETURNED'):
    pass

class NullValueNotAllowedExt(OperationalError,
    code='39004', name='NULL_VALUE_NOT_ALLOWED'):
    pass

class TriggerProtocolViolated(OperationalError,
    code='39P01', name='TRIGGER_PROTOCOL_VIOLATED'):
    pass

class SrfProtocolViolated(OperationalError,
    code='39P02', name='SRF_PROTOCOL_VIOLATED'):
    pass

class EventTriggerProtocolViolated(OperationalError,
    code='39P03', name='EVENT_TRIGGER_PROTOCOL_VIOLATED'):
    pass


# Class 3B - Savepoint Exception

class SavepointException(OperationalError,
    code='3B000', name='SAVEPOINT_EXCEPTION'):
    pass

class InvalidSavepointSpecification(OperationalError,
    code='3B001', name='INVALID_SAVEPOINT_SPECIFICATION'):
    pass


# Class 3D - Invalid Catalog Name

class InvalidCatalogName(ProgrammingError,
    code='3D000', name='INVALID_CATALOG_NAME'):
    pass


# Class 3F - Invalid Schema Name

class InvalidSchemaName(ProgrammingError,
    code='3F000', name='INVALID_SCHEMA_NAME'):
    pass


# Class 40 - Transaction Rollback

class TransactionRollback(OperationalError,
    code='40000', name='TRANSACTION_ROLLBACK'):
    pass

class SerializationFailure(OperationalError,
    code='40001', name='SERIALIZATION_FAILURE'):
    pass

class TransactionIntegrityConstraintViolation(OperationalError,
    code='40002', name='TRANSACTION_INTEGRITY_CONSTRAINT_VIOLATION'):
    pass

class StatementCompletionUnknown(OperationalError,
    code='40003', name='STATEMENT_COMPLETION_UNKNOWN'):
    pass

class DeadlockDetected(OperationalError,
    code='40P01', name='DEADLOCK_DETECTED'):
    pass


# Class 42 - Syntax Error or Access Rule Violation

class SyntaxErrorOrAccessRuleViolation(ProgrammingError,
    code='42000', name='SYNTAX_ERROR_OR_ACCESS_RULE_VIOLATION'):
    pass

class InsufficientPrivilege(ProgrammingError,
    code='42501', name='INSUFFICIENT_PRIVILEGE'):
    pass

class SyntaxError(ProgrammingError,
    code='42601', name='SYNTAX_ERROR'):
    pass

class InvalidName(ProgrammingError,
    code='42602', name='INVALID_NAME'):
    pass

class InvalidColumnDefinition(ProgrammingError,
    code='42611', name='INVALID_COLUMN_DEFINITION'):
    pass

class NameTooLong(ProgrammingError,
    code='42622', name='NAME_TOO_LONG'):
    pass

class DuplicateColumn(ProgrammingError,
    code='42701', name='DUPLICATE_COLUMN'):
    pass

class AmbiguousColumn(ProgrammingError,
    code='42702', name='AMBIGUOUS_COLUMN'):
    pass

class UndefinedColumn(ProgrammingError,
    code='42703', name='UNDEFINED_COLUMN'):
    pass

class UndefinedObject(ProgrammingError,
    code='42704', name='UNDEFINED_OBJECT'):
    pass

class DuplicateObject(ProgrammingError,
    code='42710', name='DUPLICATE_OBJECT'):
    pass

class DuplicateAlias(ProgrammingError,
    code='42712', name='DUPLICATE_ALIAS'):
    pass

class DuplicateFunction(ProgrammingError,
    code='42723', name='DUPLICATE_FUNCTION'):
    pass

class AmbiguousFunction(ProgrammingError,
    code='42725', name='AMBIGUOUS_FUNCTION'):
    pass

class GroupingError(ProgrammingError,
    code='42803', name='GROUPING_ERROR'):
    pass

class DatatypeMismatch(ProgrammingError,
    code='42804', name='DATATYPE_MISMATCH'):
    pass

class WrongObjectType(ProgrammingError,
    code='42809', name='WRONG_OBJECT_TYPE'):
    pass

class InvalidForeignKey(ProgrammingError,
    code='42830', name='INVALID_FOREIGN_KEY'):
    pass

class CannotCoerce(ProgrammingError,
    code='42846', name='CANNOT_COERCE'):
    pass

class UndefinedFunction(ProgrammingError,
    code='42883', name='UNDEFINED_FUNCTION'):
    pass

class GeneratedAlways(ProgrammingError,
    code='428C9', name='GENERATED_ALWAYS'):
    pass

class ReservedName(ProgrammingError,
    code='42939', name='RESERVED_NAME'):
    pass

class UndefinedTable(ProgrammingError,
    code='42P01', name='UNDEFINED_TABLE'):
    pass

class UndefinedParameter(ProgrammingError,
    code='42P02', name='UNDEFINED_PARAMETER'):
    pass

class DuplicateCursor(ProgrammingError,
    code='42P03', name='DUPLICATE_CURSOR'):
    pass

class DuplicateDatabase(ProgrammingError,
    code='42P04', name='DUPLICATE_DATABASE'):
    pass

class DuplicatePreparedStatement(ProgrammingError,
    code='42P05', name='DUPLICATE_PREPARED_STATEMENT'):
    pass

class DuplicateSchema(ProgrammingError,
    code='42P06', name='DUPLICATE_SCHEMA'):
    pass

class DuplicateTable(ProgrammingError,
    code='42P07', name='DUPLICATE_TABLE'):
    pass

class AmbiguousParameter(ProgrammingError,
    code='42P08', name='AMBIGUOUS_PARAMETER'):
    pass

class AmbiguousAlias(ProgrammingError,
    code='42P09', name='AMBIGUOUS_ALIAS'):
    pass

class InvalidColumnReference(ProgrammingError,
    code='42P10', name='INVALID_COLUMN_REFERENCE'):
    pass

class InvalidCursorDefinition(ProgrammingError,
    code='42P11', name='INVALID_CURSOR_DEFINITION'):
    pass

class InvalidDatabaseDefinition(ProgrammingError,
    code='42P12', name='INVALID_DATABASE_DEFINITION'):
    pass

class InvalidFunctionDefinition(ProgrammingError,
    code='42P13', name='INVALID_FUNCTION_DEFINITION'):
    pass

class InvalidPreparedStatementDefinition(ProgrammingError,
    code='42P14', name='INVALID_PREPARED_STATEMENT_DEFINITION'):
    pass

class InvalidSchemaDefinition(ProgrammingError,
    code='42P15', name='INVALID_SCHEMA_DEFINITION'):
    pass

class InvalidTableDefinition(ProgrammingError,
    code='42P16', name='INVALID_TABLE_DEFINITION'):
    pass

class InvalidObjectDefinition(ProgrammingError,
    code='42P17', name='INVALID_OBJECT_DEFINITION'):
    pass

class IndeterminateDatatype(ProgrammingError,
    code='42P18', name='INDETERMINATE_DATATYPE'):
    pass

class InvalidRecursion(ProgrammingError,
    code='42P19', name='INVALID_RECURSION'):
    pass

class WindowingError(ProgrammingError,
    code='42P20', name='WINDOWING_ERROR'):
    pass

class CollationMismatch(ProgrammingError,
    code='42P21', name='COLLATION_MISMATCH'):
    pass

class IndeterminateCollation(ProgrammingError,
    code='42P22', name='INDETERMINATE_COLLATION'):
    pass


# Class 44 - WITH CHECK OPTION Violation

class WithCheckOptionViolation(ProgrammingError,
    code='44000', name='WITH_CHECK_OPTION_VIOLATION'):
    pass


# Class 53 - Insufficient Resources

class InsufficientResources(OperationalError,
    code='53000', name='INSUFFICIENT_RESOURCES'):
    pass

class DiskFull(OperationalError,
    code='53100', name='DISK_FULL'):
    pass

class OutOfMemory(OperationalError,
    code='53200', name='OUT_OF_MEMORY'):
    pass

class TooManyConnections(OperationalError,
    code='53300', name='TOO_MANY_CONNECTIONS'):
    pass

class ConfigurationLimitExceeded(OperationalError,
    code='53400', name='CONFIGURATION_LIMIT_EXCEEDED'):
    pass


# Class 54 - Program Limit Exceeded

class ProgramLimitExceeded(OperationalError,
    code='54000', name='PROGRAM_LIMIT_EXCEEDED'):
    pass

class StatementTooComplex(OperationalError,
    code='54001', name='STATEMENT_TOO_COMPLEX'):
    pass

class TooManyColumns(OperationalError,
    code='54011', name='TOO_MANY_COLUMNS'):
    pass

class TooManyArguments(OperationalError,
    code='54023', name='TOO_MANY_ARGUMENTS'):
    pass


# Class 55 - Object Not In Prerequisite State

class ObjectNotInPrerequisiteState(OperationalError,
    code='55000', name='OBJECT_NOT_IN_PREREQUISITE_STATE'):
    pass

class ObjectInUse(OperationalError,
    code='55006', name='OBJECT_IN_USE'):
    pass

class CantChangeRuntimeParam(OperationalError,
    code='55P02', name='CANT_CHANGE_RUNTIME_PARAM'):
    pass

class LockNotAvailable(OperationalError,
    code='55P03', name='LOCK_NOT_AVAILABLE'):
    pass

class UnsafeNewEnumValueUsage(OperationalError,
    code='55P04', name='UNSAFE_NEW_ENUM_VALUE_USAGE'):
    pass


# Class 57 - Operator Intervention

class OperatorIntervention(OperationalError,
    code='57000', name='OPERATOR_INTERVENTION'):
    pass

class QueryCanceled(OperationalError,
    code='57014', name='QUERY_CANCELED'):
    pass

class AdminShutdown(OperationalError,
    code='57P01', name='ADMIN_SHUTDOWN'):
    pass

class CrashShutdown(OperationalError,
    code='57P02', name='CRASH_SHUTDOWN'):
    pass

class CannotConnectNow(OperationalError,
    code='57P03', name='CANNOT_CONNECT_NOW'):
    pass

class DatabaseDropped(OperationalError,
    code='57P04', name='DATABASE_DROPPED'):
    pass

class IdleSessionTimeout(OperationalError,
    code='57P05', name='IDLE_SESSION_TIMEOUT'):
    pass


# Class 58 - System Error (errors external to PostgreSQL itself)

class SystemError(OperationalError,
    code='58000', name='SYSTEM_ERROR'):
    pass

class IoError(OperationalError,
    code='58030', name='IO_ERROR'):
    pass

class UndefinedFile(OperationalError,
    code='58P01', name='UNDEFINED_FILE'):
    pass

class DuplicateFile(OperationalError,
    code='58P02', name='DUPLICATE_FILE'):
    pass


# Class 72 - Snapshot Failure

class SnapshotTooOld(DatabaseError,
    code='72000', name='SNAPSHOT_TOO_OLD'):
    pass


# Class F0 - Configuration File Error

class ConfigFileError(OperationalError,
    code='F0000', name='CONFIG_FILE_ERROR'):
    pass

class LockFileExists(OperationalError,
    code='F0001', name='LOCK_FILE_EXISTS'):
    pass


# Class HV - Foreign Data Wrapper Error (SQL/MED)

class FdwError(OperationalError,
    code='HV000', name='FDW_ERROR'):
    pass

class FdwOutOfMemory(OperationalError,
    code='HV001', name='FDW_OUT_OF_MEMORY'):
    pass

class FdwDynamicParameterValueNeeded(OperationalError,
    code='HV002', name='FDW_DYNAMIC_PARAMETER_VALUE_NEEDED'):
    pass

class FdwInvalidDataType(OperationalError,
    code='HV004', name='FDW_INVALID_DATA_TYPE'):
    pass

class FdwColumnNameNotFound(OperationalError,
    code='HV005', name='FDW_COLUMN_NAME_NOT_FOUND'):
    pass

class FdwInvalidDataTypeDescriptors(OperationalError,
    code='HV006', name='FDW_INVALID_DATA_TYPE_DESCRIPTORS'):
    pass

class FdwInvalidColumnName(OperationalError,
    code='HV007', name='FDW_INVALID_COLUMN_NAME'):
    pass

class FdwInvalidColumnNumber(OperationalError,
    code='HV008', name='FDW_INVALID_COLUMN_NUMBER'):
    pass

class FdwInvalidUseOfNullPointer(OperationalError,
    code='HV009', name='FDW_INVALID_USE_OF_NULL_POINTER'):
    pass

class FdwInvalidStringFormat(OperationalError,
    code='HV00A', name='FDW_INVALID_STRING_FORMAT'):
    pass

class FdwInvalidHandle(OperationalError,
    code='HV00B', name='FDW_INVALID_HANDLE'):
    pass

class FdwInvalidOptionIndex(OperationalError,
    code='HV00C', name='FDW_INVALID_OPTION_INDEX'):
    pass

class FdwInvalidOptionName(OperationalError,
    code='HV00D', name='FDW_INVALID_OPTION_NAME'):
    pass

class FdwOptionNameNotFound(OperationalError,
    code='HV00J', name='FDW_OPTION_NAME_NOT_FOUND'):
    pass

class FdwReplyHandle(OperationalError,
    code='HV00K', name='FDW_REPLY_HANDLE'):
    pass

class FdwUnableToCreateExecution(OperationalError,
    code='HV00L', name='FDW_UNABLE_TO_CREATE_EXECUTION'):
    pass

class FdwUnableToCreateReply(OperationalError,
    code='HV00M', name='FDW_UNABLE_TO_CREATE_REPLY'):
    pass

class FdwUnableToEstablishConnection(OperationalError,
    code='HV00N', name='FDW_UNABLE_TO_ESTABLISH_CONNECTION'):
    pass

class FdwNoSchemas(OperationalError,
    code='HV00P', name='FDW_NO_SCHEMAS'):
    pass

class FdwSchemaNotFound(OperationalError,
    code='HV00Q', name='FDW_SCHEMA_NOT_FOUND'):
    pass

class FdwTableNotFound(OperationalError,
    code='HV00R', name='FDW_TABLE_NOT_FOUND'):
    pass

class FdwFunctionSequenceError(OperationalError,
    code='HV010', name='FDW_FUNCTION_SEQUENCE_ERROR'):
    pass

class FdwTooManyHandles(OperationalError,
    code='HV014', name='FDW_TOO_MANY_HANDLES'):
    pass

class FdwInconsistentDescriptorInformation(OperationalError,
    code='HV021', name='FDW_INCONSISTENT_DESCRIPTOR_INFORMATION'):
    pass

class FdwInvalidAttributeValue(OperationalError,
    code='HV024', name='FDW_INVALID_ATTRIBUTE_VALUE'):
    pass

class FdwInvalidStringLengthOrBufferLength(OperationalError,
    code='HV090', name='FDW_INVALID_STRING_LENGTH_OR_BUFFER_LENGTH'):
    pass

class FdwInvalidDescriptorFieldIdentifier(OperationalError,
    code='HV091', name='FDW_INVALID_DESCRIPTOR_FIELD_IDENTIFIER'):
    pass


# Class P0 - PL/pgSQL Error

class PlpgsqlError(ProgrammingError,
    code='P0000', name='PLPGSQL_ERROR'):
    pass

class RaiseException(ProgrammingError,
    code='P0001', name='RAISE_EXCEPTION'):
    pass

class NoDataFound(ProgrammingError,
    code='P0002', name='NO_DATA_FOUND'):
    pass

class TooManyRows(ProgrammingError,
    code='P0003', name='TOO_MANY_ROWS'):
    pass

class AssertFailure(ProgrammingError,
    code='P0004', name='ASSERT_FAILURE'):
    pass


# Class XX - Internal Error

class InternalError_(InternalError,
    code='XX000', name='INTERNAL_ERROR'):
    pass

class DataCorrupted(InternalError,
    code='XX001', name='DATA_CORRUPTED'):
    pass

class IndexCorrupted(InternalError,
    code='XX002', name='INDEX_CORRUPTED'):
    pass


# autogenerated: end
# fmt: on

# Don't show a complete traceback upon raising these exception.
# Usually the traceback starts from internal functions (for instance in the
# server communication callbacks) but, for the end user, it's more important
# to get the high level information about where the exception was raised, for
# instance in a certain `Cursor.execute()`.

_NO_TRACEBACK = (Error, KeyboardInterrupt, CancelledError)
