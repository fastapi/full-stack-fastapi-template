"""
Information about PostgreSQL types

These types allow to read information from the system catalog and provide
information to the adapters if needed.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, Sequence, overload

from . import errors as e
from . import sql
from .abc import AdaptContext, Query
from .rows import dict_row
from ._compat import TypeAlias, TypeVar
from ._typemod import TypeModifier
from ._encodings import conn_encoding

if TYPE_CHECKING:
    from .connection import Connection
    from ._connection_base import BaseConnection
    from .connection_async import AsyncConnection

T = TypeVar("T", bound="TypeInfo")
RegistryKey: TypeAlias = "str | int | tuple[type, int]"


class TypeInfo:
    """
    Hold information about a PostgreSQL base type.
    """

    __module__ = "psycopg.types"

    def __init__(
        self,
        name: str,
        oid: int,
        array_oid: int,
        *,
        regtype: str = "",
        delimiter: str = ",",
        typemod: type[TypeModifier] = TypeModifier,
    ):
        self.name = name
        self.oid = oid
        self.array_oid = array_oid
        self.regtype = regtype or name
        self.delimiter = delimiter
        self.typemod = typemod(oid)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__}:"
            f" {self.name} (oid: {self.oid}, array oid: {self.array_oid})>"
        )

    @overload
    @classmethod
    def fetch(
        cls: type[T], conn: Connection[Any], name: str | sql.Identifier
    ) -> T | None: ...

    @overload
    @classmethod
    async def fetch(
        cls: type[T], conn: AsyncConnection[Any], name: str | sql.Identifier
    ) -> T | None: ...

    @classmethod
    def fetch(
        cls: type[T], conn: BaseConnection[Any], name: str | sql.Identifier
    ) -> Any:
        """Query a system catalog to read information about a type."""
        from .connection import Connection
        from .connection_async import AsyncConnection

        if isinstance(name, sql.Composable):
            name = name.as_string(conn)

        if isinstance(conn, Connection):
            return cls._fetch(conn, name)
        elif isinstance(conn, AsyncConnection):
            return cls._fetch_async(conn, name)
        else:
            raise TypeError(
                f"expected Connection or AsyncConnection, got {type(conn).__name__}"
            )

    @classmethod
    def _fetch(cls: type[T], conn: Connection[Any], name: str) -> T | None:
        # This might result in a nested transaction. What we want is to leave
        # the function with the connection in the state we found (either idle
        # or intrans)
        try:
            from psycopg import Cursor

            with conn.transaction(), Cursor(conn, row_factory=dict_row) as cur:
                if conn_encoding(conn) == "ascii":
                    cur.execute("set local client_encoding to utf8")
                cur.execute(cls._get_info_query(conn), {"name": name})
                recs = cur.fetchall()
        except e.UndefinedObject:
            return None

        return cls._from_records(name, recs)

    @classmethod
    async def _fetch_async(
        cls: type[T], conn: AsyncConnection[Any], name: str
    ) -> T | None:
        try:
            from psycopg import AsyncCursor

            async with conn.transaction():
                async with AsyncCursor(conn, row_factory=dict_row) as cur:
                    if conn_encoding(conn) == "ascii":
                        await cur.execute("set local client_encoding to utf8")
                    await cur.execute(cls._get_info_query(conn), {"name": name})
                    recs = await cur.fetchall()
        except e.UndefinedObject:
            return None

        return cls._from_records(name, recs)

    @classmethod
    def _from_records(
        cls: type[T], name: str, recs: Sequence[dict[str, Any]]
    ) -> T | None:
        if len(recs) == 1:
            return cls(**recs[0])
        elif not recs:
            return None
        else:
            raise e.ProgrammingError(f"found {len(recs)} different types named {name}")

    def register(self, context: AdaptContext | None = None) -> None:
        """
        Register the type information, globally or in the specified `!context`.
        """
        if context:
            types = context.adapters.types
        else:
            from . import postgres

            types = postgres.types

        types.add(self)

        if self.array_oid:
            from .types.array import register_array

            register_array(self, context)

    @classmethod
    def _get_info_query(cls, conn: BaseConnection[Any]) -> Query:
        return sql.SQL(
            """\
SELECT
    typname AS name, oid, typarray AS array_oid,
    oid::regtype::text AS regtype, typdelim AS delimiter
FROM pg_type t
WHERE t.oid = {regtype}
ORDER BY t.oid
"""
        ).format(regtype=cls._to_regtype(conn))

    @classmethod
    def _has_to_regtype_function(cls, conn: BaseConnection[Any]) -> bool:
        # to_regtype() introduced in PostgreSQL 9.4 and CockroachDB 22.2
        info = conn.info
        if info.vendor == "PostgreSQL":
            return info.server_version >= 90400
        elif info.vendor == "CockroachDB":
            return info.server_version >= 220200
        else:
            return False

    @classmethod
    def _to_regtype(cls, conn: BaseConnection[Any]) -> sql.SQL:
        # `to_regtype()` returns the type oid or NULL, unlike the :: operator,
        # which returns the type or raises an exception, which requires
        # a transaction rollback and leaves traces in the server logs.

        if cls._has_to_regtype_function(conn):
            return sql.SQL("to_regtype(%(name)s)")
        else:
            return sql.SQL("%(name)s::regtype")

    def _added(self, registry: TypesRegistry) -> None:
        """Method called by the `!registry` when the object is added there."""
        pass

    def get_type_display(self, oid: int | None = None, fmod: int | None = None) -> str:
        parts = []
        parts.append(self.name)
        mod = self.typemod.get_modifier(fmod) if fmod is not None else ()
        if mod:
            parts.append(f"({','.join(map(str, mod))})")

        if oid == self.array_oid:
            parts.append("[]")

        return "".join(parts)

    def get_display_size(self, fmod: int) -> int | None:
        return self.typemod.get_display_size(fmod)

    def get_precision(self, fmod: int) -> int | None:
        return self.typemod.get_precision(fmod)

    def get_scale(self, fmod: int) -> int | None:
        return self.typemod.get_scale(fmod)


class TypesRegistry:
    """
    Container for the information about types in a database.
    """

    __module__ = "psycopg.types"

    def __init__(self, template: TypesRegistry | None = None):
        self._registry: dict[RegistryKey, TypeInfo]

        # Make a shallow copy: it will become a proper copy if the registry
        # is edited.
        if template:
            self._registry = template._registry
            self._own_state = False
            template._own_state = False
        else:
            self.clear()

    def clear(self) -> None:
        self._registry = {}
        self._own_state = True

    def add(self, info: TypeInfo) -> None:
        self._ensure_own_state()
        if info.oid:
            self._registry[info.oid] = info
        if info.array_oid:
            self._registry[info.array_oid] = info
        self._registry[info.name] = info

        if info.regtype and info.regtype not in self._registry:
            self._registry[info.regtype] = info

        # Allow info to customise further their relation with the registry
        info._added(self)

    def __iter__(self) -> Iterator[TypeInfo]:
        seen = set()
        for t in self._registry.values():
            if id(t) not in seen:
                seen.add(id(t))
                yield t

    @overload
    def __getitem__(self, key: str | int) -> TypeInfo: ...

    @overload
    def __getitem__(self, key: tuple[type[T], int]) -> T: ...

    def __getitem__(self, key: RegistryKey) -> TypeInfo:
        """
        Return info about a type, specified by name or oid

        :param key: the name or oid of the type to look for.

        Raise KeyError if not found.
        """
        if isinstance(key, str):
            if key.endswith("[]"):
                key = key[:-2]
        elif not isinstance(key, (int, tuple)):
            raise TypeError(f"the key must be an oid or a name, got {type(key)}")
        try:
            return self._registry[key]
        except KeyError:
            raise KeyError(f"couldn't find the type {key!r} in the types registry")

    @overload
    def get(self, key: str | int) -> TypeInfo | None: ...

    @overload
    def get(self, key: tuple[type[T], int]) -> T | None: ...

    def get(self, key: RegistryKey) -> TypeInfo | None:
        """
        Return info about a type, specified by name or oid

        :param key: the name or oid of the type to look for.

        Unlike `__getitem__`, return None if not found.
        """
        try:
            return self[key]
        except KeyError:
            return None

    def get_oid(self, name: str) -> int:
        """
        Return the oid of a PostgreSQL type by name.

        :param key: the name of the type to look for.

        Return the array oid if the type ends with "``[]``"

        Raise KeyError if the name is unknown.
        """
        t = self[name]
        if name.endswith("[]"):
            return t.array_oid
        else:
            return t.oid

    def get_by_subtype(self, cls: type[T], subtype: int | str) -> T | None:
        """
        Return info about a `TypeInfo` subclass by its element name or oid.

        :param cls: the subtype of `!TypeInfo` to look for. Currently
            supported are `~psycopg.types.range.RangeInfo` and
            `~psycopg.types.multirange.MultirangeInfo`.
        :param subtype: The name or OID of the subtype of the element to look for.
        :return: The `!TypeInfo` object of class `!cls` whose subtype is
            `!subtype`. `!None` if the element or its range are not found.
        """
        try:
            info = self[subtype]
        except KeyError:
            return None
        return self.get((cls, info.oid))

    def _ensure_own_state(self) -> None:
        # Time to write! so, copy.
        if not self._own_state:
            self._registry = self._registry.copy()
            self._own_state = True
