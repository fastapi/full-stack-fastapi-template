"""
Transaction context managers returned by Connection.transaction()
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import logging
from types import TracebackType
from typing import TYPE_CHECKING, Any, Generic, Iterator

from . import errors as e
from . import pq, sql
from .abc import ConnectionType, PQGen
from ._compat import Self
from .pq.misc import connection_summary

if TYPE_CHECKING:
    from .connection import Connection
    from .connection_async import AsyncConnection

IDLE = pq.TransactionStatus.IDLE

OK = pq.ConnStatus.OK

logger = logging.getLogger(__name__)


class Rollback(Exception):
    """
    Exit the current `Transaction` context immediately and rollback any changes
    made within this context.

    If a transaction context is specified in the constructor, rollback
    enclosing transactions contexts up to and including the one specified.
    """

    __module__ = "psycopg"

    def __init__(self, transaction: Transaction | AsyncTransaction | None = None):
        self.transaction = transaction

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.transaction!r})"


class OutOfOrderTransactionNesting(e.ProgrammingError):
    """Out-of-order transaction nesting detected"""


class BaseTransaction(Generic[ConnectionType]):
    def __init__(
        self,
        connection: ConnectionType,
        savepoint_name: str | None = None,
        force_rollback: bool = False,
    ):
        self._conn = connection
        self.pgconn = self._conn.pgconn
        self._savepoint_name = savepoint_name or ""
        self.force_rollback = force_rollback
        self._entered = self._exited = False
        self._outer_transaction = False
        self._stack_index = -1

    @property
    def savepoint_name(self) -> str | None:
        """
        The name of the savepoint; `!None` if handling the main transaction.
        """
        # Yes, it may change on __enter__. No, I don't care, because the
        # un-entered state is outside the public interface.
        return self._savepoint_name

    def __repr__(self) -> str:
        cls = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        info = connection_summary(self.pgconn)
        if not self._entered:
            status = "inactive"
        elif not self._exited:
            status = "active"
        else:
            status = "terminated"

        sp = f"{self.savepoint_name!r} " if self.savepoint_name else ""
        return f"<{cls} {sp}({status}) {info} at 0x{id(self):x}>"

    def _enter_gen(self) -> PQGen[None]:
        if self._entered:
            raise TypeError("transaction blocks can be used only once")
        self._entered = True

        self._push_savepoint()
        for command in self._get_enter_commands():
            yield from self._conn._exec_command(command)

    def _exit_gen(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> PQGen[bool]:
        if not exc_val and not self.force_rollback:
            yield from self._commit_gen()
            return False
        else:
            # try to rollback, but if there are problems (connection in a bad
            # state) just warn without clobbering the exception bubbling up.
            try:
                return (yield from self._rollback_gen(exc_val))
            except OutOfOrderTransactionNesting:
                # Clobber an exception happened in the block with the exception
                # caused by out-of-order transaction detected, so make the
                # behaviour consistent with _commit_gen and to make sure the
                # user fixes this condition, which is unrelated from
                # operational error that might arise in the block.
                raise
            except Exception as exc2:
                logger.warning("error ignored in rollback of %s: %s", self, exc2)
                return False

    def _commit_gen(self) -> PQGen[None]:
        ex = self._pop_savepoint("commit")
        self._exited = True
        if ex:
            raise ex

        for command in self._get_commit_commands():
            yield from self._conn._exec_command(command)

    def _rollback_gen(self, exc_val: BaseException | None) -> PQGen[bool]:
        if isinstance(exc_val, Rollback):
            logger.debug(f"{self._conn}: Explicit rollback from: ", exc_info=True)

        ex = self._pop_savepoint("rollback")
        self._exited = True
        if ex:
            raise ex

        for command in self._get_rollback_commands():
            yield from self._conn._exec_command(command)

        # Also clear the prepared statements cache.
        self._conn._prepared.clear()
        yield from self._conn._prepared.maintain_gen(self._conn)

        if isinstance(exc_val, Rollback):
            if not exc_val.transaction or exc_val.transaction is self:
                return True  # Swallow the exception

        return False

    def _get_enter_commands(self) -> Iterator[bytes]:
        if self._outer_transaction:
            yield self._conn._get_tx_start_command()

        if self._savepoint_name:
            yield (
                sql.SQL("SAVEPOINT {}")
                .format(sql.Identifier(self._savepoint_name))
                .as_bytes(self._conn)
            )

    def _get_commit_commands(self) -> Iterator[bytes]:
        if self._savepoint_name and not self._outer_transaction:
            yield (
                sql.SQL("RELEASE {}")
                .format(sql.Identifier(self._savepoint_name))
                .as_bytes(self._conn)
            )

        if self._outer_transaction:
            assert not self._conn._num_transactions
            yield b"COMMIT"

    def _get_rollback_commands(self) -> Iterator[bytes]:
        if self._savepoint_name and not self._outer_transaction:
            yield (
                sql.SQL("ROLLBACK TO {n}")
                .format(n=sql.Identifier(self._savepoint_name))
                .as_bytes(self._conn)
            )
            yield (
                sql.SQL("RELEASE {n}")
                .format(n=sql.Identifier(self._savepoint_name))
                .as_bytes(self._conn)
            )

        if self._outer_transaction:
            assert not self._conn._num_transactions
            yield b"ROLLBACK"

    def _push_savepoint(self) -> None:
        """
        Push the transaction on the connection transactions stack.

        Also set the internal state of the object and verify consistency.
        """
        self._outer_transaction = self.pgconn.transaction_status == IDLE
        if self._outer_transaction:
            # outer transaction: if no name it's only a begin, else
            # there will be an additional savepoint
            assert not self._conn._num_transactions
        else:
            # inner transaction: it always has a name
            if not self._savepoint_name:
                self._savepoint_name = f"_pg3_{self._conn._num_transactions + 1}"

        self._stack_index = self._conn._num_transactions
        self._conn._num_transactions += 1

    def _pop_savepoint(self, action: str) -> Exception | None:
        """
        Pop the transaction from the connection transactions stack.

        Also verify the state consistency.
        """
        self._conn._num_transactions -= 1
        if self._conn._num_transactions == self._stack_index:
            return None

        return OutOfOrderTransactionNesting(
            f"transaction {action} at the wrong nesting level: {self}"
        )


class Transaction(BaseTransaction["Connection[Any]"]):
    """
    Returned by `Connection.transaction()` to handle a transaction block.
    """

    __module__ = "psycopg"

    @property
    def connection(self) -> Connection[Any]:
        """The connection the object is managing."""
        return self._conn

    def __enter__(self) -> Self:
        with self._conn.lock:
            self._conn.wait(self._enter_gen())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if self.pgconn.status == OK:
            with self._conn.lock:
                return self._conn.wait(self._exit_gen(exc_type, exc_val, exc_tb))
        else:
            return False


class AsyncTransaction(BaseTransaction["AsyncConnection[Any]"]):
    """
    Returned by `AsyncConnection.transaction()` to handle a transaction block.
    """

    __module__ = "psycopg"

    @property
    def connection(self) -> AsyncConnection[Any]:
        return self._conn

    async def __aenter__(self) -> Self:
        async with self._conn.lock:
            await self._conn.wait(self._enter_gen())
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if self.pgconn.status == OK:
            async with self._conn.lock:
                return await self._conn.wait(self._exit_gen(exc_type, exc_val, exc_tb))
        else:
            return False
