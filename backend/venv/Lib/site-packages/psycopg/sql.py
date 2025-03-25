"""
SQL composition utility module
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import codecs
import string
from abc import ABC, abstractmethod
from typing import Any, Iterable, Iterator, Sequence

from .pq import Escaping
from .abc import AdaptContext
from ._enums import PyFormat
from ._compat import LiteralString
from ._encodings import conn_encoding
from ._transformer import Transformer


def quote(obj: Any, context: AdaptContext | None = None) -> str:
    """
    Adapt a Python object to a quoted SQL string.

    Use this function only if you absolutely want to convert a Python string to
    an SQL quoted literal to use e.g. to generate batch SQL and you won't have
    a connection available when you will need to use it.

    This function is relatively inefficient, because it doesn't cache the
    adaptation rules. If you pass a `!context` you can adapt the adaptation
    rules used, otherwise only global rules are used.

    """
    return Literal(obj).as_string(context)


class Composable(ABC):
    """
    Abstract base class for objects that can be used to compose an SQL string.

    `!Composable` objects can be joined using the ``+`` operator: the result
    will be a `Composed` instance containing the objects joined. The operator
    ``*`` is also supported with an integer argument: the result is a
    `!Composed` instance containing the left argument repeated as many times as
    requested.

    `!SQL` and `!Composed` objects can be passed directly to
    `~psycopg.Cursor.execute()`, `~psycopg.Cursor.executemany()`,
    `~psycopg.Cursor.copy()` in place of the query string.
    """

    def __init__(self, obj: Any):
        self._obj = obj

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._obj!r})"

    @abstractmethod
    def as_bytes(self, context: AdaptContext | None = None) -> bytes:
        """
        Return the value of the object as bytes.

        :param context: the context to evaluate the object into.
        :type context: `connection` or `cursor`

        The method is automatically invoked by `~psycopg.Cursor.execute()`,
        `~psycopg.Cursor.executemany()`, `~psycopg.Cursor.copy()` if a
        `!Composable` is passed instead of the query string.

        """
        raise NotImplementedError

    def as_string(self, context: AdaptContext | None = None) -> str:
        """
        Return the value of the object as string.

        :param context: the context to evaluate the string into.
        :type context: `connection` or `cursor`

        """
        conn = context.connection if context else None
        enc = conn_encoding(conn)
        b = self.as_bytes(context)
        if isinstance(b, bytes):
            return b.decode(enc)
        else:
            # buffer object
            return codecs.lookup(enc).decode(b)[0]

    def __add__(self, other: Composable) -> Composed:
        if isinstance(other, Composed):
            return Composed([self]) + other
        if isinstance(other, Composable):
            return Composed([self]) + Composed([other])
        else:
            return NotImplemented

    def __mul__(self, n: int) -> Composed:
        return Composed([self] * n)

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self._obj == other._obj

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class Composed(Composable):
    """
    A `Composable` object made of a sequence of `!Composable`.

    The object is usually created using `!Composable` operators and methods
    (such as the `SQL.format()` method). `!Composed` objects can be passed
    directly to `~psycopg.Cursor.execute()`, `~psycopg.Cursor.executemany()`,
    `~psycopg.Cursor.copy()` in place of the query string.

    It is also possible to create a `!Composed` directly specifying a sequence
    of objects as arguments: if they are not `!Composable` they will be wrapped
    in a `Literal`.

    Example::

        >>> comp = sql.Composed(
        ...     [sql.SQL("INSERT INTO "), sql.Identifier("table")])
        >>> print(comp.as_string(conn))
        INSERT INTO "table"

    `!Composed` objects are iterable (so they can be used in `SQL.join` for
    instance).
    """

    _obj: list[Composable]

    def __init__(self, seq: Sequence[Any]):
        seq = [obj if isinstance(obj, Composable) else Literal(obj) for obj in seq]
        super().__init__(seq)

    def as_bytes(self, context: AdaptContext | None = None) -> bytes:
        return b"".join(obj.as_bytes(context) for obj in self._obj)

    def __iter__(self) -> Iterator[Composable]:
        return iter(self._obj)

    def __add__(self, other: Composable) -> Composed:
        if isinstance(other, Composed):
            return Composed(self._obj + other._obj)
        if isinstance(other, Composable):
            return Composed(self._obj + [other])
        else:
            return NotImplemented

    def join(self, joiner: SQL | LiteralString) -> Composed:
        """
        Return a new `!Composed` interposing the `!joiner` with the `!Composed` items.

        The `!joiner` must be a `SQL` or a string which will be interpreted as
        an `SQL`.

        Example::

            >>> fields = sql.Identifier('foo') + sql.Identifier('bar')  # a Composed
            >>> print(fields.join(', ').as_string(conn))
            "foo", "bar"

        """
        if isinstance(joiner, str):
            joiner = SQL(joiner)
        elif not isinstance(joiner, SQL):
            raise TypeError(
                "Composed.join() argument must be strings or SQL,"
                f" got {joiner!r} instead"
            )

        return joiner.join(self._obj)


class SQL(Composable):
    """
    A `Composable` representing a snippet of SQL statement.

    `!SQL` exposes `join()` and `format()` methods useful to create a template
    where to merge variable parts of a query (for instance field or table
    names).

    The `!obj` string doesn't undergo any form of escaping, so it is not
    suitable to represent variable identifiers or values: you should only use
    it to pass constant strings representing templates or snippets of SQL
    statements; use other objects such as `Identifier` or `Literal` to
    represent variable parts.

    `!SQL` objects can be passed directly to `~psycopg.Cursor.execute()`,
    `~psycopg.Cursor.executemany()`, `~psycopg.Cursor.copy()` in place of the
    query string.

    Example::

        >>> query = sql.SQL("SELECT {0} FROM {1}").format(
        ...    sql.SQL(', ').join([sql.Identifier('foo'), sql.Identifier('bar')]),
        ...    sql.Identifier('table'))
        >>> print(query.as_string(conn))
        SELECT "foo", "bar" FROM "table"
    """

    _obj: LiteralString
    _formatter = string.Formatter()

    def __init__(self, obj: LiteralString):
        super().__init__(obj)
        if not isinstance(obj, str):
            raise TypeError(f"SQL values must be strings, got {obj!r} instead")

    def as_string(self, context: AdaptContext | None = None) -> str:
        return self._obj

    def as_bytes(self, context: AdaptContext | None = None) -> bytes:
        conn = context.connection if context else None
        enc = conn_encoding(conn)
        return self._obj.encode(enc)

    def format(self, *args: Any, **kwargs: Any) -> Composed:
        """
        Merge `Composable` objects into a template.

        :param args: parameters to replace to numbered (``{0}``, ``{1}``) or
            auto-numbered (``{}``) placeholders
        :param kwargs: parameters to replace to named (``{name}``) placeholders
        :return: the union of the `!SQL` string with placeholders replaced
        :rtype: `Composed`

        The method is similar to the Python `str.format()` method: the string
        template supports auto-numbered (``{}``), numbered (``{0}``,
        ``{1}``...), and named placeholders (``{name}``), with positional
        arguments replacing the numbered placeholders and keywords replacing
        the named ones. However placeholder modifiers (``{0!r}``, ``{0:<10}``)
        are not supported.

        If a `!Composable` objects is passed to the template it will be merged
        according to its `as_string()` method. If any other Python object is
        passed, it will be wrapped in a `Literal` object and so escaped
        according to SQL rules.

        Example::

            >>> print(sql.SQL("SELECT * FROM {} WHERE {} = %s")
            ...     .format(sql.Identifier('people'), sql.Identifier('id'))
            ...     .as_string(conn))
            SELECT * FROM "people" WHERE "id" = %s

            >>> print(sql.SQL("SELECT * FROM {tbl} WHERE name = {name}")
            ...     .format(tbl=sql.Identifier('people'), name="O'Rourke"))
            ...     .as_string(conn))
            SELECT * FROM "people" WHERE name = 'O''Rourke'

        """
        rv: list[Composable] = []
        autonum: int | None = 0
        # TODO: this is probably not the right way to whitelist pre
        # pyre complains. Will wait for mypy to complain too to fix.
        pre: LiteralString
        for pre, name, spec, conv in self._formatter.parse(self._obj):
            if spec:
                raise ValueError("no format specification supported by SQL")
            if conv:
                raise ValueError("no format conversion supported by SQL")
            if pre:
                rv.append(SQL(pre))

            if name is None:
                continue

            if name.isdigit():
                if autonum:
                    raise ValueError(
                        "cannot switch from automatic field numbering to manual"
                    )
                rv.append(args[int(name)])
                autonum = None

            elif not name:
                if autonum is None:
                    raise ValueError(
                        "cannot switch from manual field numbering to automatic"
                    )
                rv.append(args[autonum])
                autonum += 1

            else:
                rv.append(kwargs[name])

        return Composed(rv)

    def join(self, seq: Iterable[Composable]) -> Composed:
        """
        Join a sequence of `Composable`.

        :param seq: the elements to join.
        :type seq: iterable of `!Composable`

        Use the `!SQL` object's string to separate the elements in `!seq`.
        Note that `Composed` objects are iterable too, so they can be used as
        argument for this method.

        Example::

            >>> snip = sql.SQL(', ').join(
            ...     sql.Identifier(n) for n in ['foo', 'bar', 'baz'])
            >>> print(snip.as_string(conn))
            "foo", "bar", "baz"
        """
        rv = []
        it = iter(seq)
        try:
            rv.append(next(it))
        except StopIteration:
            pass
        else:
            for i in it:
                rv.append(self)
                rv.append(i)

        return Composed(rv)


class Identifier(Composable):
    """
    A `Composable` representing an SQL identifier or a dot-separated sequence.

    Identifiers usually represent names of database objects, such as tables or
    fields. PostgreSQL identifiers follow `different rules`__ than SQL string
    literals for escaping (e.g. they use double quotes instead of single).

    .. __: https://www.postgresql.org/docs/current/sql-syntax-lexical.html# \
        SQL-SYNTAX-IDENTIFIERS

    Example::

        >>> t1 = sql.Identifier("foo")
        >>> t2 = sql.Identifier("ba'r")
        >>> t3 = sql.Identifier('ba"z')
        >>> print(sql.SQL(', ').join([t1, t2, t3]).as_string(conn))
        "foo", "ba'r", "ba""z"

    Multiple strings can be passed to the object to represent a qualified name,
    i.e. a dot-separated sequence of identifiers.

    Example::

        >>> query = sql.SQL("SELECT {} FROM {}").format(
        ...     sql.Identifier("table", "field"),
        ...     sql.Identifier("schema", "table"))
        >>> print(query.as_string(conn))
        SELECT "table"."field" FROM "schema"."table"

    """

    _obj: Sequence[str]

    def __init__(self, *strings: str):
        # init super() now to make the __repr__ not explode in case of error
        super().__init__(strings)

        if not strings:
            raise TypeError("Identifier cannot be empty")

        for s in strings:
            if not isinstance(s, str):
                raise TypeError(
                    f"SQL identifier parts must be strings, got {s!r} instead"
                )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(repr, self._obj))})"

    def as_bytes(self, context: AdaptContext | None = None) -> bytes:
        conn = context.connection if context else None
        if conn:
            esc = Escaping(conn.pgconn)
            enc = conn_encoding(conn)
            escs = [esc.escape_identifier(s.encode(enc)) for s in self._obj]
        else:
            escs = [self._escape_identifier(s.encode()) for s in self._obj]
        return b".".join(escs)

    def _escape_identifier(self, s: bytes) -> bytes:
        """
        Approximation of PQescapeIdentifier taking no connection.
        """
        return b'"' + s.replace(b'"', b'""') + b'"'


class Literal(Composable):
    """
    A `Composable` representing an SQL value to include in a query.

    Usually you will want to include placeholders in the query and pass values
    as `~cursor.execute()` arguments. If however you really really need to
    include a literal value in the query you can use this object.

    The string returned by `!as_string()` follows the normal :ref:`adaptation
    rules <types-adaptation>` for Python objects.

    Example::

        >>> s1 = sql.Literal("fo'o")
        >>> s2 = sql.Literal(42)
        >>> s3 = sql.Literal(date(2000, 1, 1))
        >>> print(sql.SQL(', ').join([s1, s2, s3]).as_string(conn))
        'fo''o', 42, '2000-01-01'::date

    """

    def as_bytes(self, context: AdaptContext | None = None) -> bytes:
        tx = Transformer.from_context(context)
        return tx.as_literal(self._obj)


class Placeholder(Composable):
    """A `Composable` representing a placeholder for query parameters.

    If the name is specified, generate a named placeholder (e.g. ``%(name)s``,
    ``%(name)b``), otherwise generate a positional placeholder (e.g. ``%s``,
    ``%b``).

    The object is useful to generate SQL queries with a variable number of
    arguments.

    Examples::

        >>> names = ['foo', 'bar', 'baz']

        >>> q1 = sql.SQL("INSERT INTO my_table ({}) VALUES ({})").format(
        ...     sql.SQL(', ').join(map(sql.Identifier, names)),
        ...     sql.SQL(', ').join(sql.Placeholder() * len(names)))
        >>> print(q1.as_string(conn))
        INSERT INTO my_table ("foo", "bar", "baz") VALUES (%s, %s, %s)

        >>> q2 = sql.SQL("INSERT INTO my_table ({}) VALUES ({})").format(
        ...     sql.SQL(', ').join(map(sql.Identifier, names)),
        ...     sql.SQL(', ').join(map(sql.Placeholder, names)))
        >>> print(q2.as_string(conn))
        INSERT INTO my_table ("foo", "bar", "baz") VALUES (%(foo)s, %(bar)s, %(baz)s)

    """

    def __init__(self, name: str = "", format: str | PyFormat = PyFormat.AUTO):
        super().__init__(name)
        if not isinstance(name, str):
            raise TypeError(f"expected string as name, got {name!r}")

        if ")" in name:
            raise ValueError(f"invalid name: {name!r}")

        if type(format) is str:
            format = PyFormat(format)
        if not isinstance(format, PyFormat):
            raise TypeError(
                f"expected PyFormat as format, got {type(format).__name__!r}"
            )

        self._format: PyFormat = format

    def __repr__(self) -> str:
        parts = []
        if self._obj:
            parts.append(repr(self._obj))
        if self._format is not PyFormat.AUTO:
            parts.append(f"format={self._format.name}")

        return f"{self.__class__.__name__}({', '.join(parts)})"

    def as_string(self, context: AdaptContext | None = None) -> str:
        code = self._format.value
        return f"%({self._obj}){code}" if self._obj else f"%{code}"

    def as_bytes(self, context: AdaptContext | None = None) -> bytes:
        conn = context.connection if context else None
        enc = conn_encoding(conn)
        return self.as_string(context).encode(enc)


# Literals
NULL = SQL("NULL")
DEFAULT = SQL("DEFAULT")
