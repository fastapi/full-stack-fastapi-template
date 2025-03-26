"""
Adapters for arrays
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import re
import struct
from math import prod
from typing import Any, Callable, Pattern, cast

from .. import errors as e
from .. import postgres, pq
from ..abc import AdaptContext, Buffer, Dumper, DumperKey, Loader, NoneType, Transformer
from .._oids import INVALID_OID, TEXT_ARRAY_OID, TEXT_OID
from ..adapt import PyFormat, RecursiveDumper, RecursiveLoader
from .._compat import cache
from .._struct import pack_len, unpack_len
from .._cmodule import _psycopg
from .._typeinfo import TypeInfo

_struct_head = struct.Struct("!III")  # ndims, hasnull, elem oid
_pack_head = cast(Callable[[int, int, int], bytes], _struct_head.pack)
_unpack_head = cast(
    Callable[[Buffer], "tuple[int, int, int]"], _struct_head.unpack_from
)
_struct_dim = struct.Struct("!II")  # dim, lower bound
_pack_dim = cast(Callable[[int, int], bytes], _struct_dim.pack)
_unpack_dim = cast(Callable[[Buffer, int], "tuple[int, int]"], _struct_dim.unpack_from)

PY_TEXT = PyFormat.TEXT
PQ_BINARY = pq.Format.BINARY


class BaseListDumper(RecursiveDumper):
    element_oid = INVALID_OID

    def __init__(self, cls: type, context: AdaptContext | None = None):
        if cls is NoneType:
            cls = list

        super().__init__(cls, context)
        self.sub_dumper: Dumper | None = None
        if self.element_oid and context:
            sdclass = context.adapters.get_dumper_by_oid(self.element_oid, self.format)
            self.sub_dumper = sdclass(NoneType, context)

    def _find_list_element(self, L: list[Any], format: PyFormat) -> Any:
        """
        Find the first non-null element of an eventually nested list
        """
        items = list(self._flatiter(L, set()))
        types = {type(item): item for item in items}
        if not types:
            return None

        if len(types) == 1:
            t, v = types.popitem()
        else:
            # More than one type in the list. It might be still good, as long
            # as they dump with the same oid (e.g. IPv4Network, IPv6Network).
            dumpers = [self._tx.get_dumper(item, format) for item in types.values()]
            oids = {d.oid for d in dumpers}
            if len(oids) == 1:
                t, v = types.popitem()
            else:
                raise e.DataError(
                    "cannot dump lists of mixed types;"
                    f" got: {', '.join(sorted(t.__name__ for t in types))}"
                )

        # Checking for precise type. If the type is a subclass (e.g. Int4)
        # we assume the user knows what type they are passing.
        if t is not int:
            return v

        # If we got an int, let's see what is the biggest one in order to
        # choose the smallest OID and allow Postgres to do the right cast.
        imax: int = max(items)
        imin: int = min(items)
        if imin >= 0:
            return imax
        else:
            return max(imax, -imin - 1)

    def _flatiter(self, L: list[Any], seen: set[int]) -> Any:
        if id(L) in seen:
            raise e.DataError("cannot dump a recursive list")

        seen.add(id(L))

        for item in L:
            if type(item) is list:
                yield from self._flatiter(item, seen)
            elif item is not None:
                yield item

        return None

    def _get_base_type_info(self, base_oid: int) -> TypeInfo:
        """
        Return info about the base type.

        Return text info as fallback.
        """
        if base_oid:
            info = self._tx.adapters.types.get(base_oid)
            if info:
                return info

        return self._tx.adapters.types["text"]


class ListDumper(BaseListDumper):
    delimiter = b","

    def get_key(self, obj: list[Any], format: PyFormat) -> DumperKey:
        if self.oid:
            return self.cls

        item = self._find_list_element(obj, format)
        if item is None:
            return self.cls

        sd = self._tx.get_dumper(item, format)
        return (self.cls, sd.get_key(item, format))

    def upgrade(self, obj: list[Any], format: PyFormat) -> BaseListDumper:
        # If we have an oid we don't need to upgrade
        if self.oid:
            return self

        item = self._find_list_element(obj, format)
        if item is None:
            # Empty lists can only be dumped as text if the type is unknown.
            return self

        sd = self._tx.get_dumper(item, PyFormat.from_pq(self.format))
        dumper = type(self)(self.cls, self._tx)
        dumper.sub_dumper = sd

        # We consider an array of unknowns as unknown, so we can dump empty
        # lists or lists containing only None elements.
        if sd.oid != INVALID_OID:
            info = self._get_base_type_info(sd.oid)
            dumper.oid = info.array_oid or TEXT_ARRAY_OID
            dumper.delimiter = info.delimiter.encode()
        else:
            dumper.oid = INVALID_OID

        return dumper

    # Double quotes and backslashes embedded in element values will be
    # backslash-escaped.
    _re_esc = re.compile(rb'(["\\])')

    def dump(self, obj: list[Any]) -> Buffer | None:
        tokens: list[Buffer] = []
        needs_quotes = _get_needs_quotes_regexp(self.delimiter).search

        def dump_list(obj: list[Any]) -> None:
            if not obj:
                tokens.append(b"{}")
                return

            tokens.append(b"{")
            for item in obj:
                if isinstance(item, list):
                    dump_list(item)
                elif item is not None:
                    ad = self._dump_item(item)
                    if ad is None:
                        tokens.append(b"NULL")
                    else:
                        if needs_quotes(ad):
                            if not isinstance(ad, bytes):
                                ad = bytes(ad)
                            ad = b'"' + self._re_esc.sub(rb"\\\1", ad) + b'"'
                        tokens.append(ad)
                else:
                    tokens.append(b"NULL")

                tokens.append(self.delimiter)

            tokens[-1] = b"}"

        dump_list(obj)

        return b"".join(tokens)

    def _dump_item(self, item: Any) -> Buffer | None:
        if self.sub_dumper:
            return self.sub_dumper.dump(item)
        else:
            return self._tx.get_dumper(item, PY_TEXT).dump(item)


@cache
def _get_needs_quotes_regexp(delimiter: bytes) -> Pattern[bytes]:
    """Return a regexp to recognise when a value needs quotes

    from https://www.postgresql.org/docs/current/arrays.html#ARRAYS-IO

    The array output routine will put double quotes around element values if
    they are empty strings, contain curly braces, delimiter characters,
    double quotes, backslashes, or white space, or match the word NULL.
    """
    return re.compile(
        rb"""(?xi)
          ^$              # the empty string
        | ["{}%s\\\s]      # or a char to escape
        | ^null$          # or the word NULL
        """
        % delimiter
    )


class ListBinaryDumper(BaseListDumper):
    format = pq.Format.BINARY

    def get_key(self, obj: list[Any], format: PyFormat) -> DumperKey:
        if self.oid:
            return self.cls

        item = self._find_list_element(obj, format)
        if item is None:
            return (self.cls,)

        sd = self._tx.get_dumper(item, format)
        return (self.cls, sd.get_key(item, format))

    def upgrade(self, obj: list[Any], format: PyFormat) -> BaseListDumper:
        # If we have an oid we don't need to upgrade
        if self.oid:
            return self

        item = self._find_list_element(obj, format)
        if item is None:
            return ListDumper(self.cls, self._tx)

        sd = self._tx.get_dumper(item, format.from_pq(self.format))
        dumper = type(self)(self.cls, self._tx)
        dumper.sub_dumper = sd
        info = self._get_base_type_info(sd.oid)
        dumper.oid = info.array_oid or TEXT_ARRAY_OID

        return dumper

    def dump(self, obj: list[Any]) -> Buffer | None:
        # Postgres won't take unknown for element oid: fall back on text
        sub_oid = self.sub_dumper and self.sub_dumper.oid or TEXT_OID

        if not obj:
            return _pack_head(0, 0, sub_oid)

        data: list[Buffer] = [b"", b""]  # placeholders to avoid a resize
        dims: list[int] = []
        hasnull = 0

        def calc_dims(L: list[Any]) -> None:
            if isinstance(L, self.cls):
                if not L:
                    raise e.DataError("lists cannot contain empty lists")
                dims.append(len(L))
                calc_dims(L[0])

        calc_dims(obj)

        def dump_list(L: list[Any], dim: int) -> None:
            nonlocal hasnull
            if len(L) != dims[dim]:
                raise e.DataError("nested lists have inconsistent lengths")

            if dim == len(dims) - 1:
                for item in L:
                    if item is not None:
                        # If we get here, the sub_dumper must have been set
                        item = self.sub_dumper.dump(item)  # type: ignore[union-attr]
                    if item is not None:
                        data.append(pack_len(len(item)))
                        data.append(item)
                    else:
                        hasnull = 1
                        data.append(b"\xff\xff\xff\xff")
            else:
                for item in L:
                    if not isinstance(item, self.cls):
                        raise e.DataError("nested lists have inconsistent depths")
                    dump_list(item, dim + 1)  # type: ignore

        dump_list(obj, 0)

        data[0] = _pack_head(len(dims), hasnull, sub_oid)
        data[1] = b"".join(_pack_dim(dim, 1) for dim in dims)
        return b"".join(data)


class ArrayLoader(RecursiveLoader):
    delimiter = b","
    base_oid: int

    def load(self, data: Buffer) -> list[Any]:
        loader = self._tx.get_loader(self.base_oid, self.format)
        return _load_text(data, loader, self.delimiter)


class ArrayBinaryLoader(RecursiveLoader):
    format = pq.Format.BINARY

    def load(self, data: Buffer) -> list[Any]:
        return _load_binary(data, self._tx)


def register_array(info: TypeInfo, context: AdaptContext | None = None) -> None:
    if not info.array_oid:
        raise ValueError(f"the type info {info} doesn't describe an array")

    adapters = context.adapters if context else postgres.adapters

    loader = _make_loader(info.name, info.oid, info.delimiter)
    adapters.register_loader(info.array_oid, loader)

    # No need to make a new loader because the binary datum has all the info.
    loader = getattr(_psycopg, "ArrayBinaryLoader", ArrayBinaryLoader)
    adapters.register_loader(info.array_oid, loader)

    dumper = _make_dumper(info.name, info.oid, info.array_oid, info.delimiter)
    adapters.register_dumper(None, dumper)

    dumper = _make_binary_dumper(info.name, info.oid, info.array_oid)
    adapters.register_dumper(None, dumper)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_loader(name: str, oid: int, delimiter: str) -> type[Loader]:
    # Note: caching this function is really needed because, if the C extension
    # is available, the resulting type cannot be GC'd, so calling
    # register_array() in a loop results in a leak. See #647.
    base = getattr(_psycopg, "ArrayLoader", ArrayLoader)
    attribs = {"base_oid": oid, "delimiter": delimiter.encode()}
    return type(f"{name.title()}{base.__name__}", (base,), attribs)


@cache
def _make_dumper(
    name: str, oid: int, array_oid: int, delimiter: str
) -> type[BaseListDumper]:
    attribs = {"oid": array_oid, "element_oid": oid, "delimiter": delimiter.encode()}
    return type(f"{name.title()}ListDumper", (ListDumper,), attribs)


@cache
def _make_binary_dumper(name: str, oid: int, array_oid: int) -> type[BaseListDumper]:
    attribs = {"oid": array_oid, "element_oid": oid}
    return type(f"{name.title()}ListBinaryDumper", (ListBinaryDumper,), attribs)


def register_default_adapters(context: AdaptContext) -> None:
    # The text dumper is more flexible as it can handle lists of mixed type,
    # so register it later.
    context.adapters.register_dumper(list, ListBinaryDumper)
    context.adapters.register_dumper(list, ListDumper)


def register_all_arrays(context: AdaptContext) -> None:
    """
    Associate the array oid of all the types in Loader.globals.

    This function is designed to be called once at import time, after having
    registered all the base loaders.
    """
    for t in context.adapters.types:
        if t.array_oid:
            t.register(context)


def _load_text(
    data: Buffer,
    loader: Loader,
    delimiter: bytes = b",",
    __re_unescape: Pattern[bytes] = re.compile(rb"\\(.)"),
) -> list[Any]:
    rv = None
    stack: list[Any] = []
    a: list[Any] = []
    rv = a
    load = loader.load

    # Remove the dimensions information prefix (``[...]=``)
    if data and data[0] == b"["[0]:
        if isinstance(data, memoryview):
            data = bytes(data)
        idx = data.find(b"=")
        if idx == -1:
            raise e.DataError("malformed array: no '=' after dimension information")
        data = data[idx + 1 :]

    re_parse = _get_array_parse_regexp(delimiter)
    for m in re_parse.finditer(data):
        t = m.group(1)
        if t == b"{":
            if stack:
                stack[-1].append(a)
            stack.append(a)
            a = []

        elif t == b"}":
            if not stack:
                raise e.DataError("malformed array: unexpected '}'")
            rv = stack.pop()

        else:
            if not stack:
                wat = t[:10].decode("utf8", "replace") + "..." if len(t) > 10 else ""
                raise e.DataError(f"malformed array: unexpected '{wat}'")
            if t == b"NULL":
                v = None
            else:
                if t.startswith(b'"'):
                    t = __re_unescape.sub(rb"\1", t[1:-1])
                v = load(t)

            stack[-1].append(v)

    assert rv is not None
    return rv


@cache
def _get_array_parse_regexp(delimiter: bytes) -> Pattern[bytes]:
    """
    Return a regexp to tokenize an array representation into item and brackets
    """
    return re.compile(
        rb"""(?xi)
        (     [{}]                        # open or closed bracket
            | " (?: [^"\\] | \\. )* "     # or a quoted string
            | [^"{}%s\\]+                 # or an unquoted non-empty string
        ) ,?
        """
        % delimiter
    )


def _load_binary(data: Buffer, tx: Transformer) -> list[Any]:
    ndims, hasnull, oid = _unpack_head(data)
    load = tx.get_loader(oid, PQ_BINARY).load

    if not ndims:
        return []

    p = 12 + 8 * ndims
    dims = [_unpack_dim(data, i)[0] for i in range(12, p, 8)]
    nelems = prod(dims)

    out: list[Any] = [None] * nelems
    for i in range(nelems):
        size = unpack_len(data, p)[0]
        p += 4
        if size == -1:
            continue
        out[i] = load(data[p : p + size])
        p += size

    # fon ndims > 1 we have to aggregate the array into sub-arrays
    for dim in dims[-1:0:-1]:
        out = [out[i : i + dim] for i in range(0, len(out), dim)]

    return out
