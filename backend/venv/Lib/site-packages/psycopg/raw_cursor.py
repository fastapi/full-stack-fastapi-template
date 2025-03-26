"""
psycopg raw queries cursors
"""

# Copyright (C) 2023 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING

from .abc import ConnectionType, Params, Query
from .sql import Composable
from .rows import Row
from ._enums import PyFormat
from .cursor import Cursor
from ._queries import PostgresQuery
from ._cursor_base import BaseCursor
from .cursor_async import AsyncCursor
from .server_cursor import AsyncServerCursor, ServerCursor

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from .connection import Connection  # noqa: F401
    from .connection_async import AsyncConnection  # noqa: F401


class PostgresRawQuery(PostgresQuery):
    def convert(self, query: Query, vars: Params | None) -> None:
        if isinstance(query, str):
            bquery = query.encode(self._encoding)
        elif isinstance(query, Composable):
            bquery = query.as_bytes(self._tx)
        else:
            bquery = query

        self.query = bquery
        self._want_formats = self._order = None
        self.dump(vars)

    def dump(self, vars: Params | None) -> None:
        if vars is not None:
            if not PostgresQuery.is_params_sequence(vars):
                raise TypeError("raw queries require a sequence of parameters")
            self._want_formats = [PyFormat.AUTO] * len(vars)

            self.params = self._tx.dump_sequence(vars, self._want_formats)
            self.types = self._tx.types or ()
            self.formats = self._tx.formats
        else:
            self.params = None
            self.types = ()
            self.formats = None


class RawCursorMixin(BaseCursor[ConnectionType, Row]):
    _query_cls = PostgresRawQuery


class RawCursor(RawCursorMixin["Connection[Any]", Row], Cursor[Row]):
    __module__ = "psycopg"


class AsyncRawCursor(RawCursorMixin["AsyncConnection[Any]", Row], AsyncCursor[Row]):
    __module__ = "psycopg"


class RawServerCursor(RawCursorMixin["Connection[Any]", Row], ServerCursor[Row]):
    __module__ = "psycopg"


class AsyncRawServerCursor(
    RawCursorMixin["AsyncConnection[Any]", Row], AsyncServerCursor[Row]
):
    __module__ = "psycopg"
