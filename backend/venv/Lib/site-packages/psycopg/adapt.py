"""
Entry point into the adaptation system.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from . import abc, pq

# Objects exported here
from ._enums import PyFormat as PyFormat
from ._transformer import Transformer as Transformer
from ._adapters_map import AdaptersMap as AdaptersMap  # noqa: F401 # reexport

if TYPE_CHECKING:
    from ._connection_base import BaseConnection

Buffer = abc.Buffer

ORD_BS = ord("\\")


class Dumper(abc.Dumper, ABC):
    """
    Convert Python object of the type `!cls` to PostgreSQL representation.
    """

    oid: int = 0
    """The oid to pass to the server, if known."""

    format: pq.Format = pq.Format.TEXT
    """The format of the data dumped."""

    def __init__(self, cls: type, context: abc.AdaptContext | None = None):
        self.cls = cls
        self.connection: BaseConnection[Any] | None
        self.connection = context.connection if context else None

    def __repr__(self) -> str:
        return (
            f"<{type(self).__module__}.{type(self).__qualname__}"
            f" (oid={self.oid}) at 0x{id(self):x}>"
        )

    @abstractmethod
    def dump(self, obj: Any) -> Buffer | None: ...

    def quote(self, obj: Any) -> Buffer:
        """
        By default return the `dump()` value quoted and sanitised, so
        that the result can be used to build a SQL string. This works well
        for most types and you won't likely have to implement this method in a
        subclass.
        """
        value = self.dump(obj)
        if value is None:
            return b"NULL"

        if self.connection:
            esc = pq.Escaping(self.connection.pgconn)
            # escaping and quoting
            return esc.escape_literal(value)

        # This path is taken when quote is asked without a connection,
        # usually it means by psycopg.sql.quote() or by
        # 'Composible.as_string(None)'. Most often than not this is done by
        # someone generating a SQL file to consume elsewhere.

        # No quoting, only quote escaping, random bs escaping. See further.
        esc = pq.Escaping()
        out = esc.escape_string(value)

        # b"\\" in memoryview doesn't work so search for the ascii value
        if ORD_BS not in out:
            # If the string has no backslash, the result is correct and we
            # don't need to bother with standard_conforming_strings.
            return b"'" + out + b"'"

        # The libpq has a crazy behaviour: PQescapeString uses the last
        # standard_conforming_strings setting seen on a connection. This
        # means that backslashes might be escaped or might not.
        #
        # A syntax E'\\' works everywhere, whereas E'\' is an error. OTOH,
        # if scs is off, '\\' raises a warning and '\' is an error.
        #
        # Check what the libpq does, and if it doesn't escape the backslash
        # let's do it on our own. Never mind the race condition.
        rv: bytes = b" E'" + out + b"'"
        if esc.escape_string(b"\\") == b"\\":
            rv = rv.replace(b"\\", b"\\\\")
        return rv

    def get_key(self, obj: Any, format: PyFormat) -> abc.DumperKey:
        """
        Implementation of the `~psycopg.abc.Dumper.get_key()` member of the
        `~psycopg.abc.Dumper` protocol. Look at its definition for details.

        This implementation returns the `!cls` passed in the constructor.
        Subclasses needing to specialise the PostgreSQL type according to the
        *value* of the object dumped (not only according to to its type)
        should override this class.

        """
        return self.cls

    def upgrade(self, obj: Any, format: PyFormat) -> Dumper:
        """
        Implementation of the `~psycopg.abc.Dumper.upgrade()` member of the
        `~psycopg.abc.Dumper` protocol. Look at its definition for details.

        This implementation just returns `!self`. If a subclass implements
        `get_key()` it should probably override `!upgrade()` too.
        """
        return self


class Loader(abc.Loader, ABC):
    """
    Convert PostgreSQL values with type OID `!oid` to Python objects.
    """

    format: pq.Format = pq.Format.TEXT
    """The format of the data loaded."""

    def __init__(self, oid: int, context: abc.AdaptContext | None = None):
        self.oid = oid
        self.connection: BaseConnection[Any] | None
        self.connection = context.connection if context else None

    @abstractmethod
    def load(self, data: Buffer) -> Any:
        """Convert a PostgreSQL value to a Python object."""
        ...


class RecursiveDumper(Dumper):
    """Dumper with a transformer to help dumping recursive types."""

    def __init__(self, cls: type, context: abc.AdaptContext | None = None):
        super().__init__(cls, context)
        self._tx = Transformer.from_context(context)


class RecursiveLoader(Loader):
    """Loader with a transformer to help loading recursive types."""

    def __init__(self, oid: int, context: abc.AdaptContext | None = None):
        super().__init__(oid, context)
        self._tx = Transformer.from_context(context)
