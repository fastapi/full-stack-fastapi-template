"""
dict to hstore adaptation
"""

# Copyright (C) 2021 The Psycopg Team

from __future__ import annotations

import re

from .. import errors as e
from .. import postgres
from ..abc import AdaptContext, Buffer
from .._oids import TEXT_OID
from ..adapt import PyFormat, RecursiveDumper, RecursiveLoader
from .._compat import TypeAlias, cache
from .._typeinfo import TypeInfo

_re_escape = re.compile(r'(["\\])')
_re_unescape = re.compile(r"\\(.)")

_re_hstore = re.compile(
    r"""
    # hstore key:
    # a string of normal or escaped chars
    "((?: [^"\\] | \\. )*)"
    \s*=>\s* # hstore value
    (?:
        NULL # the value can be null - not caught
        # or a quoted string like the key
        | "((?: [^"\\] | \\. )*)"
    )
    (?:\s*,\s*|$) # pairs separated by comma or end of string.
""",
    re.VERBOSE,
)


Hstore: TypeAlias = "dict[str, str | None]"


class BaseHstoreDumper(RecursiveDumper):
    def dump(self, obj: Hstore) -> Buffer | None:
        if not obj:
            return b""

        tokens: list[str] = []

        def add_token(s: str) -> None:
            tokens.append('"')
            tokens.append(_re_escape.sub(r"\\\1", s))
            tokens.append('"')

        for k, v in obj.items():
            if not isinstance(k, str):
                raise e.DataError("hstore keys can only be strings")
            add_token(k)

            tokens.append("=>")

            if v is None:
                tokens.append("NULL")
            elif not isinstance(v, str):
                raise e.DataError("hstore keys can only be strings")
            else:
                add_token(v)

            tokens.append(",")

        del tokens[-1]
        data = "".join(tokens)
        dumper = self._tx.get_dumper(data, PyFormat.TEXT)
        return dumper.dump(data)


class HstoreLoader(RecursiveLoader):
    def load(self, data: Buffer) -> Hstore:
        loader = self._tx.get_loader(TEXT_OID, self.format)
        s: str = loader.load(data)

        rv: Hstore = {}
        start = 0
        for m in _re_hstore.finditer(s):
            if m is None or m.start() != start:
                raise e.DataError(f"error parsing hstore pair at char {start}")
            k = _re_unescape.sub(r"\1", m.group(1))
            v = m.group(2)
            if v is not None:
                v = _re_unescape.sub(r"\1", v)

            rv[k] = v
            start = m.end()

        if start < len(s):
            raise e.DataError(f"error parsing hstore: unparsed data after char {start}")

        return rv


def register_hstore(info: TypeInfo, context: AdaptContext | None = None) -> None:
    """Register the adapters to load and dump hstore.

    :param info: The object with the information about the hstore type.
    :param context: The context where to register the adapters. If `!None`,
        register it globally.

    .. note::

        Registering the adapters doesn't affect objects already created, even
        if they are children of the registered context. For instance,
        registering the adapter globally doesn't affect already existing
        connections.
    """
    # A friendly error warning instead of an AttributeError in case fetch()
    # failed and it wasn't noticed.
    if not info:
        raise TypeError("no info passed. Is the 'hstore' extension loaded?")

    # Register arrays and type info
    info.register(context)

    adapters = context.adapters if context else postgres.adapters

    # Generate and register a customized text dumper
    adapters.register_dumper(dict, _make_hstore_dumper(info.oid))

    # register the text loader on the oid
    adapters.register_loader(info.oid, HstoreLoader)


# Cache all dynamically-generated types to avoid leaks in case the types
# cannot be GC'd.


@cache
def _make_hstore_dumper(oid_in: int) -> type[BaseHstoreDumper]:
    """
    Return an hstore dumper class configured using `oid_in`.

    Avoid to create new classes if the oid configured is the same.
    """

    class HstoreDumper(BaseHstoreDumper):
        oid = oid_in

    return HstoreDumper
