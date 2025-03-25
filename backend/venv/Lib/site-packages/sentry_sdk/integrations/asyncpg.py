from __future__ import annotations
import contextlib
from typing import Any, TypeVar, Callable, Awaitable, Iterator

from asyncpg.cursor import BaseCursor  # type: ignore

from sentry_sdk import Hub
from sentry_sdk.consts import OP, SPANDATA
from sentry_sdk.integrations import Integration, DidNotEnable
from sentry_sdk.tracing import Span
from sentry_sdk.tracing_utils import add_query_source, record_sql_queries
from sentry_sdk.utils import parse_version, capture_internal_exceptions

try:
    import asyncpg  # type: ignore[import-not-found]

except ImportError:
    raise DidNotEnable("asyncpg not installed.")

# asyncpg.__version__ is a string containing the semantic version in the form of "<major>.<minor>.<patch>"
asyncpg_version = parse_version(asyncpg.__version__)

if asyncpg_version is not None and asyncpg_version < (0, 23, 0):
    raise DidNotEnable("asyncpg >= 0.23.0 required")


class AsyncPGIntegration(Integration):
    identifier = "asyncpg"
    _record_params = False

    def __init__(self, *, record_params: bool = False):
        AsyncPGIntegration._record_params = record_params

    @staticmethod
    def setup_once() -> None:
        asyncpg.Connection.execute = _wrap_execute(
            asyncpg.Connection.execute,
        )

        asyncpg.Connection._execute = _wrap_connection_method(
            asyncpg.Connection._execute
        )
        asyncpg.Connection._executemany = _wrap_connection_method(
            asyncpg.Connection._executemany, executemany=True
        )
        asyncpg.Connection.cursor = _wrap_cursor_creation(asyncpg.Connection.cursor)
        asyncpg.Connection.prepare = _wrap_connection_method(asyncpg.Connection.prepare)
        asyncpg.connect_utils._connect_addr = _wrap_connect_addr(
            asyncpg.connect_utils._connect_addr
        )


T = TypeVar("T")


def _wrap_execute(f: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    async def _inner(*args: Any, **kwargs: Any) -> T:
        hub = Hub.current
        integration = hub.get_integration(AsyncPGIntegration)

        # Avoid recording calls to _execute twice.
        # Calls to Connection.execute with args also call
        # Connection._execute, which is recorded separately
        # args[0] = the connection object, args[1] is the query
        if integration is None or len(args) > 2:
            return await f(*args, **kwargs)

        query = args[1]
        with record_sql_queries(
            hub, None, query, None, None, executemany=False
        ) as span:
            res = await f(*args, **kwargs)

        with capture_internal_exceptions():
            add_query_source(hub, span)

        return res

    return _inner


SubCursor = TypeVar("SubCursor", bound=BaseCursor)


@contextlib.contextmanager
def _record(
    hub: Hub,
    cursor: SubCursor | None,
    query: str,
    params_list: tuple[Any, ...] | None,
    *,
    executemany: bool = False,
) -> Iterator[Span]:
    integration = hub.get_integration(AsyncPGIntegration)
    if not integration._record_params:
        params_list = None

    param_style = "pyformat" if params_list else None

    with record_sql_queries(
        hub,
        cursor,
        query,
        params_list,
        param_style,
        executemany=executemany,
        record_cursor_repr=cursor is not None,
    ) as span:
        yield span


def _wrap_connection_method(
    f: Callable[..., Awaitable[T]], *, executemany: bool = False
) -> Callable[..., Awaitable[T]]:
    async def _inner(*args: Any, **kwargs: Any) -> T:
        hub = Hub.current
        integration = hub.get_integration(AsyncPGIntegration)

        if integration is None:
            return await f(*args, **kwargs)

        query = args[1]
        params_list = args[2] if len(args) > 2 else None
        with _record(hub, None, query, params_list, executemany=executemany) as span:
            _set_db_data(span, args[0])
            res = await f(*args, **kwargs)

        return res

    return _inner


def _wrap_cursor_creation(f: Callable[..., T]) -> Callable[..., T]:
    def _inner(*args: Any, **kwargs: Any) -> T:  # noqa: N807
        hub = Hub.current
        integration = hub.get_integration(AsyncPGIntegration)

        if integration is None:
            return f(*args, **kwargs)

        query = args[1]
        params_list = args[2] if len(args) > 2 else None

        with _record(
            hub,
            None,
            query,
            params_list,
            executemany=False,
        ) as span:
            _set_db_data(span, args[0])
            res = f(*args, **kwargs)
            span.set_data("db.cursor", res)

        return res

    return _inner


def _wrap_connect_addr(f: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    async def _inner(*args: Any, **kwargs: Any) -> T:
        hub = Hub.current
        integration = hub.get_integration(AsyncPGIntegration)

        if integration is None:
            return await f(*args, **kwargs)

        user = kwargs["params"].user
        database = kwargs["params"].database

        with hub.start_span(op=OP.DB, description="connect") as span:
            span.set_data(SPANDATA.DB_SYSTEM, "postgresql")
            addr = kwargs.get("addr")
            if addr:
                try:
                    span.set_data(SPANDATA.SERVER_ADDRESS, addr[0])
                    span.set_data(SPANDATA.SERVER_PORT, addr[1])
                except IndexError:
                    pass
            span.set_data(SPANDATA.DB_NAME, database)
            span.set_data(SPANDATA.DB_USER, user)

            with capture_internal_exceptions():
                hub.add_breadcrumb(message="connect", category="query", data=span._data)
            res = await f(*args, **kwargs)

        return res

    return _inner


def _set_db_data(span: Span, conn: Any) -> None:
    span.set_data(SPANDATA.DB_SYSTEM, "postgresql")

    addr = conn._addr
    if addr:
        try:
            span.set_data(SPANDATA.SERVER_ADDRESS, addr[0])
            span.set_data(SPANDATA.SERVER_PORT, addr[1])
        except IndexError:
            pass

    database = conn._params.database
    if database:
        span.set_data(SPANDATA.DB_NAME, database)

    user = conn._params.user
    if user:
        span.set_data(SPANDATA.DB_USER, user)
