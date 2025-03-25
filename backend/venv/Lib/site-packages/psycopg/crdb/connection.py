"""
CockroachDB-specific connections.
"""

# Copyright (C) 2022 The Psycopg Team

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from .. import errors as e
from ..rows import Row
from ._types import adapters
from ..connection import Connection
from .._adapters_map import AdaptersMap
from .._connection_info import ConnectionInfo
from ..connection_async import AsyncConnection

if TYPE_CHECKING:
    from ..pq.abc import PGconn


class _CrdbConnectionMixin:
    _adapters: AdaptersMap | None
    pgconn: PGconn

    @classmethod
    def is_crdb(cls, conn: Connection[Any] | AsyncConnection[Any] | PGconn) -> bool:
        """
        Return `!True` if the server connected to `!conn` is CockroachDB.
        """
        if isinstance(conn, (Connection, AsyncConnection)):
            conn = conn.pgconn

        return bool(conn.parameter_status(b"crdb_version"))

    @property
    def adapters(self) -> AdaptersMap:
        if not self._adapters:
            # By default, use CockroachDB adapters map
            self._adapters = AdaptersMap(adapters)

        return self._adapters

    @property
    def info(self) -> CrdbConnectionInfo:
        return CrdbConnectionInfo(self.pgconn)

    def _check_tpc(self) -> None:
        if self.is_crdb(self.pgconn):
            raise e.NotSupportedError("CockroachDB doesn't support prepared statements")


class CrdbConnection(_CrdbConnectionMixin, Connection[Row]):
    """
    Wrapper for a connection to a CockroachDB database.
    """

    __module__ = "psycopg.crdb"


class AsyncCrdbConnection(_CrdbConnectionMixin, AsyncConnection[Row]):
    """
    Wrapper for an async connection to a CockroachDB database.
    """

    __module__ = "psycopg.crdb"


class CrdbConnectionInfo(ConnectionInfo):
    """
    `~psycopg.ConnectionInfo` subclass to get info about a CockroachDB database.
    """

    __module__ = "psycopg.crdb"

    @property
    def vendor(self) -> str:
        return "CockroachDB"

    @property
    def server_version(self) -> int:
        """
        Return the CockroachDB server version connected.

        Return a number in the PostgreSQL format (e.g. 21.2.10 -> 210210).
        """
        sver = self.parameter_status("crdb_version")
        if not sver:
            raise e.InternalError("'crdb_version' parameter status not set")

        ver = self.parse_crdb_version(sver)
        if ver is None:
            raise e.InterfaceError(f"couldn't parse CockroachDB version from: {sver!r}")

        return ver

    @classmethod
    def parse_crdb_version(self, sver: str) -> int | None:
        m = re.search(r"\bv(\d+)\.(\d+)\.(\d+)", sver)
        if not m:
            return None

        return int(m.group(1)) * 10000 + int(m.group(2)) * 100 + int(m.group(3))
