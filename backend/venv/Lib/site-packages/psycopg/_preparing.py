"""
Support for prepared statements
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, Sequence
from collections import OrderedDict

from . import pq
from .abc import PQGen
from ._compat import Deque, TypeAlias
from ._queries import PostgresQuery

if TYPE_CHECKING:
    from .pq.abc import PGresult
    from ._connection_base import BaseConnection

Key: TypeAlias = "tuple[bytes, tuple[int, ...]]"

COMMAND_OK = pq.ExecStatus.COMMAND_OK
TUPLES_OK = pq.ExecStatus.TUPLES_OK


class Prepare(IntEnum):
    NO = auto()
    YES = auto()
    SHOULD = auto()


class PrepareManager:
    # Number of times a query is executed before it is prepared.
    prepare_threshold: int | None = 5

    # Maximum number of prepared statements on the connection.
    prepared_max: int = 100

    def __init__(self) -> None:
        # Map (query, types) to the number of times the query was seen.
        self._counts: OrderedDict[Key, int] = OrderedDict()

        # Map (query, types) to the name of the statement if  prepared.
        self._names: OrderedDict[Key, bytes] = OrderedDict()

        # Counter to generate prepared statements names
        self._prepared_idx = 0

        self._to_flush = Deque["bytes | None"]()

    @staticmethod
    def key(query: PostgresQuery) -> Key:
        return (query.query, query.types)

    def get(
        self, query: PostgresQuery, prepare: bool | None = None
    ) -> tuple[Prepare, bytes]:
        """
        Check if a query is prepared, tell back whether to prepare it.
        """
        if prepare is False or self.prepare_threshold is None:
            # The user doesn't want this query to be prepared
            return Prepare.NO, b""

        key = self.key(query)
        name = self._names.get(key)
        if name:
            # The query was already prepared in this session
            return Prepare.YES, name

        count = self._counts.get(key, 0)
        if count >= self.prepare_threshold or prepare:
            # The query has been executed enough times and needs to be prepared
            name = f"_pg3_{self._prepared_idx}".encode()
            self._prepared_idx += 1
            return Prepare.SHOULD, name
        else:
            # The query is not to be prepared yet
            return Prepare.NO, b""

    def _should_discard(self, prep: Prepare, results: Sequence[PGresult]) -> bool:
        """Check if we need to discard our entire state: it should happen on
        rollback or on dropping objects, because the same object may get
        recreated and postgres would fail internal lookups.
        """
        if self._names or prep == Prepare.SHOULD:
            for result in results:
                if result.status != COMMAND_OK:
                    continue
                cmdstat = result.command_status
                if cmdstat and (cmdstat.startswith(b"DROP ") or cmdstat == b"ROLLBACK"):
                    return self.clear()
        return False

    @staticmethod
    def _check_results(results: Sequence[PGresult]) -> bool:
        """Return False if 'results' are invalid for prepared statement cache."""
        if len(results) != 1:
            # We cannot prepare a multiple statement
            return False

        status = results[0].status
        if COMMAND_OK != status != TUPLES_OK:
            # We don't prepare failed queries or other weird results
            return False

        return True

    def _rotate(self) -> None:
        """Evict an old value from the cache.

        If it was prepared, deallocate it. Do it only once: if the cache was
        resized, deallocate gradually.
        """
        if len(self._counts) > self.prepared_max:
            self._counts.popitem(last=False)

        if len(self._names) > self.prepared_max:
            name = self._names.popitem(last=False)[1]
            self._to_flush.append(name)

    def maybe_add_to_cache(
        self, query: PostgresQuery, prep: Prepare, name: bytes
    ) -> Key | None:
        """Handle 'query' for possible addition to the cache.

        If a new entry has been added, return its key. Return None otherwise
        (meaning the query is already in cache or cache is not enabled).
        """
        # don't do anything if prepared statements are disabled
        if self.prepare_threshold is None:
            return None

        key = self.key(query)
        if key in self._counts:
            if prep is Prepare.SHOULD:
                del self._counts[key]
                self._names[key] = name
            else:
                self._counts[key] += 1
                self._counts.move_to_end(key)
            return None

        elif key in self._names:
            self._names.move_to_end(key)
            return None

        else:
            if prep is Prepare.SHOULD:
                self._names[key] = name
            else:
                self._counts[key] = 1
            return key

    def validate(
        self,
        key: Key,
        prep: Prepare,
        name: bytes,
        results: Sequence[PGresult],
    ) -> None:
        """Validate cached entry with 'key' by checking query 'results'.

        Possibly record a command to perform maintenance on database side.
        """
        if self._should_discard(prep, results):
            return

        if not self._check_results(results):
            self._names.pop(key, None)
            self._counts.pop(key, None)
        else:
            self._rotate()

    def clear(self) -> bool:
        """Clear the cache of the maintenance commands.

        Clear the internal state and prepare a command to clear the state of
        the server.
        """
        self._counts.clear()
        if self._names:
            self._names.clear()
            self._to_flush.clear()
            self._to_flush.append(None)
            return True
        else:
            return False

    def maintain_gen(self, conn: BaseConnection[Any]) -> PQGen[None]:
        """
        Generator to send the commands to perform periodic maintenance

        Deallocate unneeded command in the server, or flush the prepared
        statements server state entirely if necessary.
        """
        while self._to_flush:
            name = self._to_flush.popleft()
            yield from conn._deallocate(name)
