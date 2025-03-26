"""
Helper object to transform values between Python and PostgreSQL

Python implementation of the object. Use the `_transformer module to import
the right implementation (Python or C). The public place where the object
is exported is `psycopg.adapt` (which we may not use to avoid circular
dependencies problems).
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, DefaultDict, Sequence
from collections import defaultdict

from . import abc
from . import errors as e
from . import pq
from .abc import AdaptContext, Buffer, LoadFunc, NoneType, PyFormat
from .rows import Row, RowMaker
from ._oids import INVALID_OID, TEXT_OID
from ._compat import TypeAlias
from ._encodings import conn_encoding

if TYPE_CHECKING:
    from .abc import DumperKey  # noqa: F401
    from .adapt import AdaptersMap
    from .pq.abc import PGresult
    from ._connection_base import BaseConnection

DumperCache: TypeAlias = "dict[DumperKey, abc.Dumper]"
OidDumperCache: TypeAlias = "dict[int, abc.Dumper]"
LoaderCache: TypeAlias = "dict[int, abc.Loader]"

TEXT = pq.Format.TEXT
PY_TEXT = PyFormat.TEXT


class Transformer(AdaptContext):
    """
    An object that can adapt efficiently between Python and PostgreSQL.

    The life cycle of the object is the query, so it is assumed that attributes
    such as the server version or the connection encoding will not change. The
    object have its state so adapting several values of the same type can be
    optimised.

    """

    __module__ = "psycopg.adapt"

    __slots__ = """
        types formats
        _conn _adapters _pgresult _dumpers _loaders _encoding _none_oid
        _oid_dumpers _oid_types _row_dumpers _row_loaders
        """.split()

    types: tuple[int, ...] | None
    formats: list[pq.Format] | None

    _adapters: AdaptersMap
    _pgresult: PGresult | None
    _none_oid: int

    def __init__(self, context: AdaptContext | None = None):
        self._pgresult = self.types = self.formats = None

        # WARNING: don't store context, or you'll create a loop with the Cursor
        if context:
            self._adapters = context.adapters
            self._conn = context.connection
        else:
            from . import postgres

            self._adapters = postgres.adapters
            self._conn = None

        # mapping fmt, class -> Dumper instance
        self._dumpers: DefaultDict[PyFormat, DumperCache]
        self._dumpers = defaultdict(dict)

        # mapping fmt, oid -> Dumper instance
        # Not often used, so create it only if needed.
        self._oid_dumpers: tuple[OidDumperCache, OidDumperCache] | None
        self._oid_dumpers = None

        # mapping fmt, oid -> Loader instance
        self._loaders: tuple[LoaderCache, LoaderCache] = ({}, {})

        self._row_dumpers: list[abc.Dumper] | None = None

        # sequence of load functions from value to python
        # the length of the result columns
        self._row_loaders: list[LoadFunc] = []

        # mapping oid -> type sql representation
        self._oid_types: dict[int, bytes] = {}

        self._encoding = ""

    @classmethod
    def from_context(cls, context: AdaptContext | None) -> Transformer:
        """
        Return a Transformer from an AdaptContext.

        If the context is a Transformer instance, just return it.
        """
        if isinstance(context, Transformer):
            return context
        else:
            return cls(context)

    @property
    def connection(self) -> BaseConnection[Any] | None:
        return self._conn

    @property
    def encoding(self) -> str:
        if not self._encoding:
            self._encoding = conn_encoding(self.connection)
        return self._encoding

    @property
    def adapters(self) -> AdaptersMap:
        return self._adapters

    @property
    def pgresult(self) -> PGresult | None:
        return self._pgresult

    def set_pgresult(
        self,
        result: PGresult | None,
        *,
        set_loaders: bool = True,
        format: pq.Format | None = None,
    ) -> None:
        self._pgresult = result

        if not result:
            self._nfields = self._ntuples = 0
            if set_loaders:
                self._row_loaders = []
            return

        self._ntuples = result.ntuples
        nf = self._nfields = result.nfields

        if not set_loaders:
            return

        if not nf:
            self._row_loaders = []
            return

        fmt: pq.Format
        fmt = result.fformat(0) if format is None else format  # type: ignore
        self._row_loaders = [
            self.get_loader(result.ftype(i), fmt).load for i in range(nf)
        ]

    def set_dumper_types(self, types: Sequence[int], format: pq.Format) -> None:
        self._row_dumpers = [self.get_dumper_by_oid(oid, format) for oid in types]
        self.types = tuple(types)
        self.formats = [format] * len(types)

    def set_loader_types(self, types: Sequence[int], format: pq.Format) -> None:
        self._row_loaders = [self.get_loader(oid, format).load for oid in types]

    def dump_sequence(
        self, params: Sequence[Any], formats: Sequence[PyFormat]
    ) -> Sequence[Buffer | None]:
        nparams = len(params)
        out: list[Buffer | None] = [None] * nparams

        # If we have dumpers, it means set_dumper_types had been called, in
        # which case self.types and self.formats are set to sequences of the
        # right size.
        if self._row_dumpers:
            for i in range(nparams):
                param = params[i]
                if param is not None:
                    out[i] = self._row_dumpers[i].dump(param)
            return out

        types = [self._get_none_oid()] * nparams
        pqformats = [TEXT] * nparams

        for i in range(nparams):
            param = params[i]
            if param is None:
                continue
            dumper = self.get_dumper(param, formats[i])
            out[i] = dumper.dump(param)
            types[i] = dumper.oid
            pqformats[i] = dumper.format

        self.types = tuple(types)
        self.formats = pqformats

        return out

    def as_literal(self, obj: Any) -> bytes:
        dumper = self.get_dumper(obj, PY_TEXT)
        rv = dumper.quote(obj)
        # If the result is quoted, and the oid not unknown or text,
        # add an explicit type cast.
        # Check the last char because the first one might be 'E'.
        oid = dumper.oid
        if oid and rv and rv[-1] == b"'"[0] and oid != TEXT_OID:
            try:
                type_sql = self._oid_types[oid]
            except KeyError:
                ti = self.adapters.types.get(oid)
                if ti:
                    if oid < 8192:
                        # builtin: prefer "timestamptz" to "timestamp with time zone"
                        type_sql = ti.name.encode(self.encoding)
                    else:
                        type_sql = ti.regtype.encode(self.encoding)
                    if oid == ti.array_oid:
                        type_sql += b"[]"
                else:
                    type_sql = b""
                self._oid_types[oid] = type_sql

            if type_sql:
                rv = b"%s::%s" % (rv, type_sql)

        if not isinstance(rv, bytes):
            rv = bytes(rv)
        return rv

    def get_dumper(self, obj: Any, format: PyFormat) -> abc.Dumper:
        """
        Return a Dumper instance to dump `!obj`.
        """
        # Normally, the type of the object dictates how to dump it
        key = type(obj)

        # Reuse an existing Dumper class for objects of the same type
        cache = self._dumpers[format]
        try:
            dumper = cache[key]
        except KeyError:
            # If it's the first time we see this type, look for a dumper
            # configured for it.
            try:
                dcls = self.adapters.get_dumper(key, format)
            except e.ProgrammingError as ex:
                raise ex from None
            else:
                cache[key] = dumper = dcls(key, self)

        # Check if the dumper requires an upgrade to handle this specific value
        key1 = dumper.get_key(obj, format)
        if key1 is key:
            return dumper

        # If it does, ask the dumper to create its own upgraded version
        try:
            return cache[key1]
        except KeyError:
            dumper = cache[key1] = dumper.upgrade(obj, format)
            return dumper

    def _get_none_oid(self) -> int:
        try:
            return self._none_oid
        except AttributeError:
            pass

        try:
            rv = self._none_oid = self._adapters.get_dumper(NoneType, PY_TEXT).oid
        except KeyError:
            raise e.InterfaceError("None dumper not found")

        return rv

    def get_dumper_by_oid(self, oid: int, format: pq.Format) -> abc.Dumper:
        """
        Return a Dumper to dump an object to the type with given oid.
        """
        if not self._oid_dumpers:
            self._oid_dumpers = ({}, {})

        # Reuse an existing Dumper class for objects of the same type
        cache = self._oid_dumpers[format]
        try:
            return cache[oid]
        except KeyError:
            # If it's the first time we see this type, look for a dumper
            # configured for it.
            dcls = self.adapters.get_dumper_by_oid(oid, format)
            cache[oid] = dumper = dcls(NoneType, self)

        return dumper

    def load_rows(self, row0: int, row1: int, make_row: RowMaker[Row]) -> list[Row]:
        res = self._pgresult
        if not res:
            raise e.InterfaceError("result not set")

        if not (0 <= row0 <= self._ntuples and 0 <= row1 <= self._ntuples):
            raise e.InterfaceError(
                f"rows must be included between 0 and {self._ntuples}"
            )

        records = []
        for row in range(row0, row1):
            record: list[Any] = [None] * self._nfields
            for col in range(self._nfields):
                val = res.get_value(row, col)
                if val is not None:
                    record[col] = self._row_loaders[col](val)
            records.append(make_row(record))

        return records

    def load_row(self, row: int, make_row: RowMaker[Row]) -> Row | None:
        res = self._pgresult
        if not res:
            return None

        if not 0 <= row < self._ntuples:
            return None

        record: list[Any] = [None] * self._nfields
        for col in range(self._nfields):
            val = res.get_value(row, col)
            if val is not None:
                record[col] = self._row_loaders[col](val)

        return make_row(record)

    def load_sequence(self, record: Sequence[Buffer | None]) -> tuple[Any, ...]:
        if len(self._row_loaders) != len(record):
            raise e.ProgrammingError(
                f"cannot load sequence of {len(record)} items:"
                f" {len(self._row_loaders)} loaders registered"
            )

        return tuple(
            (self._row_loaders[i](val) if val is not None else None)
            for i, val in enumerate(record)
        )

    def get_loader(self, oid: int, format: pq.Format) -> abc.Loader:
        try:
            return self._loaders[format][oid]
        except KeyError:
            pass

        loader_cls = self._adapters.get_loader(oid, format)
        if not loader_cls:
            loader_cls = self._adapters.get_loader(INVALID_OID, format)
            if not loader_cls:
                raise e.InterfaceError("unknown oid loader not found")
        loader = self._loaders[format][oid] = loader_cls(oid, self)
        return loader
