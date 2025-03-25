"""
Adapters for JSON types.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import json
from typing import Any, Callable

from .. import _oids, abc
from .. import errors as e
from ..pq import Format
from ..adapt import AdaptersMap, Buffer, Dumper, Loader, PyFormat
from ..errors import DataError
from .._compat import TypeAlias, cache

JsonDumpsFunction: TypeAlias = Callable[[Any], "str | bytes"]
JsonLoadsFunction: TypeAlias = Callable[["str | bytes"], Any]


def set_json_dumps(
    dumps: JsonDumpsFunction, context: abc.AdaptContext | None = None
) -> None:
    """
    Set the JSON serialisation function to store JSON objects in the database.

    :param dumps: The dump function to use.
    :type dumps: `!Callable[[Any], str]`
    :param context: Where to use the `!dumps` function. If not specified, use it
        globally.
    :type context: `~psycopg.Connection` or `~psycopg.Cursor`

    By default dumping JSON uses the builtin `json.dumps`. You can override
    it to use a different JSON library or to use customised arguments.

    If the `Json` wrapper specified a `!dumps` function, use it in precedence
    of the one set by this function.
    """
    if context is None:
        # If changing load function globally, just change the default on the
        # global class
        _JsonDumper._dumps = dumps
    else:
        adapters = context.adapters

        # If the scope is smaller than global, create subclassess and register
        # them in the appropriate scope.
        grid = [
            (Json, PyFormat.BINARY),
            (Json, PyFormat.TEXT),
            (Jsonb, PyFormat.BINARY),
            (Jsonb, PyFormat.TEXT),
        ]
        for wrapper, format in grid:
            base = _get_current_dumper(adapters, wrapper, format)
            dumper = _make_dumper(base, dumps)
            adapters.register_dumper(wrapper, dumper)


def set_json_loads(
    loads: JsonLoadsFunction, context: abc.AdaptContext | None = None
) -> None:
    """
    Set the JSON parsing function to fetch JSON objects from the database.

    :param loads: The load function to use.
    :type loads: `!Callable[[bytes], Any]`
    :param context: Where to use the `!loads` function. If not specified, use
        it globally.
    :type context: `~psycopg.Connection` or `~psycopg.Cursor`

    By default loading JSON uses the builtin `json.loads`. You can override
    it to use a different JSON library or to use customised arguments.
    """
    if context is None:
        # If changing load function globally, just change the default on the
        # global class
        _JsonLoader._loads = loads
    else:
        # If the scope is smaller than global, create subclassess and register
        # them in the appropriate scope.
        grid = [
            ("json", JsonLoader),
            ("json", JsonBinaryLoader),
            ("jsonb", JsonbLoader),
            ("jsonb", JsonbBinaryLoader),
        ]
        for tname, base in grid:
            loader = _make_loader(base, loads)
            context.adapters.register_loader(tname, loader)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_dumper(base: type[abc.Dumper], dumps: JsonDumpsFunction) -> type[abc.Dumper]:
    name = base.__name__
    if not name.startswith("Custom"):
        name = f"Custom{name}"
    return type(name, (base,), {"_dumps": dumps})


@cache
def _make_loader(base: type[Loader], loads: JsonLoadsFunction) -> type[Loader]:
    name = base.__name__
    if not name.startswith("Custom"):
        name = f"Custom{name}"
    return type(name, (base,), {"_loads": loads})


class _JsonWrapper:
    __slots__ = ("obj", "dumps")

    def __init__(self, obj: Any, dumps: JsonDumpsFunction | None = None):
        self.obj = obj
        self.dumps = dumps

    def __repr__(self) -> str:
        sobj = repr(self.obj)
        if len(sobj) > 40:
            sobj = f"{sobj[:35]} ... ({len(sobj)} chars)"
        return f"{self.__class__.__name__}({sobj})"


class Json(_JsonWrapper):
    __slots__ = ()


class Jsonb(_JsonWrapper):
    __slots__ = ()


class _JsonDumper(Dumper):
    # The globally used JSON dumps() function. It can be changed globally (by
    # set_json_dumps) or by a subclass.
    _dumps: JsonDumpsFunction = json.dumps

    def __init__(self, cls: type, context: abc.AdaptContext | None = None):
        super().__init__(cls, context)
        self.dumps = self.__class__._dumps

    def dump(self, obj: Any) -> Buffer | None:
        if isinstance(obj, _JsonWrapper):
            dumps = obj.dumps or self.dumps
            obj = obj.obj
        else:
            dumps = self.dumps
        data = dumps(obj)
        if isinstance(data, str):
            return data.encode()
        return data


class JsonDumper(_JsonDumper):
    oid = _oids.JSON_OID


class JsonBinaryDumper(_JsonDumper):
    format = Format.BINARY
    oid = _oids.JSON_OID


class JsonbDumper(_JsonDumper):
    oid = _oids.JSONB_OID


class JsonbBinaryDumper(_JsonDumper):
    format = Format.BINARY
    oid = _oids.JSONB_OID

    def dump(self, obj: Any) -> Buffer | None:
        obj_bytes = super().dump(obj)
        if obj_bytes is not None:
            return b"\x01" + obj_bytes
        else:
            return None


class _JsonLoader(Loader):
    # The globally used JSON loads() function. It can be changed globally (by
    # set_json_loads) or by a subclass.
    _loads: JsonLoadsFunction = json.loads

    def __init__(self, oid: int, context: abc.AdaptContext | None = None):
        super().__init__(oid, context)
        self.loads = self.__class__._loads

    def load(self, data: Buffer) -> Any:
        # json.loads() cannot work on memoryview.
        if not isinstance(data, bytes):
            data = bytes(data)
        return self.loads(data)


class JsonLoader(_JsonLoader):
    pass


class JsonbLoader(_JsonLoader):
    pass


class JsonBinaryLoader(_JsonLoader):
    format = Format.BINARY


class JsonbBinaryLoader(_JsonLoader):
    format = Format.BINARY

    def load(self, data: Buffer) -> Any:
        if data and data[0] != 1:
            raise DataError("unknown jsonb binary format: {data[0]}")
        data = data[1:]
        if not isinstance(data, bytes):
            data = bytes(data)
        return self.loads(data)


def _get_current_dumper(
    adapters: AdaptersMap, cls: type, format: PyFormat
) -> type[abc.Dumper]:
    try:
        return adapters.get_dumper(cls, format)
    except e.ProgrammingError:
        return _default_dumpers[cls, format]


_default_dumpers: dict[tuple[type[_JsonWrapper], PyFormat], type[Dumper]] = {
    (Json, PyFormat.BINARY): JsonBinaryDumper,
    (Json, PyFormat.TEXT): JsonDumper,
    (Jsonb, PyFormat.BINARY): JsonbBinaryDumper,
    (Jsonb, PyFormat.TEXT): JsonDumper,
}


def register_default_adapters(context: abc.AdaptContext) -> None:
    adapters = context.adapters

    # Currently json binary format is nothing different than text, maybe with
    # an extra memcopy we can avoid.
    adapters.register_dumper(Json, JsonBinaryDumper)
    adapters.register_dumper(Json, JsonDumper)
    adapters.register_dumper(Jsonb, JsonbBinaryDumper)
    adapters.register_dumper(Jsonb, JsonbDumper)
    adapters.register_loader("json", JsonLoader)
    adapters.register_loader("jsonb", JsonbLoader)
    adapters.register_loader("json", JsonBinaryLoader)
    adapters.register_loader("jsonb", JsonbBinaryLoader)
