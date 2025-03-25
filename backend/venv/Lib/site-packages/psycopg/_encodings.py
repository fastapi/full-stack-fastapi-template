"""
Mappings between PostgreSQL and Python encodings.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import re
import codecs
import string
from typing import TYPE_CHECKING, Any

from .errors import NotSupportedError
from ._compat import cache
from .pq._enums import ConnStatus

if TYPE_CHECKING:
    from ._connection_base import BaseConnection

OK = ConnStatus.OK


_py_codecs = {
    "BIG5": "big5",
    "EUC_CN": "gb2312",
    "EUC_JIS_2004": "euc_jis_2004",
    "EUC_JP": "euc_jp",
    "EUC_KR": "euc_kr",
    # "EUC_TW": not available in Python
    "GB18030": "gb18030",
    "GBK": "gbk",
    "ISO_8859_5": "iso8859-5",
    "ISO_8859_6": "iso8859-6",
    "ISO_8859_7": "iso8859-7",
    "ISO_8859_8": "iso8859-8",
    "JOHAB": "johab",
    "KOI8R": "koi8-r",
    "KOI8U": "koi8-u",
    "LATIN1": "iso8859-1",
    "LATIN10": "iso8859-16",
    "LATIN2": "iso8859-2",
    "LATIN3": "iso8859-3",
    "LATIN4": "iso8859-4",
    "LATIN5": "iso8859-9",
    "LATIN6": "iso8859-10",
    "LATIN7": "iso8859-13",
    "LATIN8": "iso8859-14",
    "LATIN9": "iso8859-15",
    # "MULE_INTERNAL": not available in Python
    "SHIFT_JIS_2004": "shift_jis_2004",
    "SJIS": "shift_jis",
    # this actually means no encoding, see PostgreSQL docs
    # it is special-cased by the text loader.
    "SQL_ASCII": "ascii",
    "UHC": "cp949",
    "UTF8": "utf-8",
    "WIN1250": "cp1250",
    "WIN1251": "cp1251",
    "WIN1252": "cp1252",
    "WIN1253": "cp1253",
    "WIN1254": "cp1254",
    "WIN1255": "cp1255",
    "WIN1256": "cp1256",
    "WIN1257": "cp1257",
    "WIN1258": "cp1258",
    "WIN866": "cp866",
    "WIN874": "cp874",
}

py_codecs: dict[bytes, str] = {}
py_codecs.update((k.encode(), v) for k, v in _py_codecs.items())

# Add an alias without underscore, for lenient lookups
py_codecs.update(
    (k.replace("_", "").encode(), v) for k, v in _py_codecs.items() if "_" in k
)

pg_codecs = {v: k.encode() for k, v in _py_codecs.items()}


def conn_encoding(conn: BaseConnection[Any] | None) -> str:
    """
    Return the Python encoding name of a psycopg connection.

    Default to utf8 if the connection has no encoding info.
    """
    return conn.pgconn._encoding if conn else "utf-8"


def conninfo_encoding(conninfo: str) -> str:
    """
    Return the Python encoding name passed in a conninfo string. Default to utf8.

    Because the input is likely to come from the user and not normalised by the
    server, be somewhat lenient (non-case-sensitive lookup, ignore noise chars).
    """
    from .conninfo import conninfo_to_dict

    params = conninfo_to_dict(conninfo)
    pgenc = params.get("client_encoding")
    if pgenc:
        try:
            return pg2pyenc(str(pgenc).encode())
        except NotSupportedError:
            pass

    return "utf-8"


@cache
def py2pgenc(name: str) -> bytes:
    """Convert a Python encoding name to PostgreSQL encoding name.

    Raise LookupError if the Python encoding is unknown.
    """
    return pg_codecs[codecs.lookup(name).name]


@cache
def pg2pyenc(name: bytes) -> str:
    """Convert a PostgreSQL encoding name to Python encoding name.

    Raise NotSupportedError if the PostgreSQL encoding is not supported by
    Python.
    """
    try:
        return py_codecs[name.replace(b"-", b"").replace(b"_", b"").upper()]
    except KeyError:
        sname = name.decode("utf8", "replace")
        raise NotSupportedError(f"codec not available in Python: {sname!r}")


def _as_python_identifier(s: str, prefix: str = "f") -> str:
    """
    Reduce a string to a valid Python identifier.

    Replace all non-valid chars with '_' and prefix the value with `!prefix` if
    the first letter is an '_'.
    """
    if not s.isidentifier():
        if s[0] in "1234567890":
            s = prefix + s
        if not s.isidentifier():
            s = _re_clean.sub("_", s)
    # namedtuple fields cannot start with underscore. So...
    if s[0] == "_":
        s = prefix + s
    return s


_re_clean = re.compile(
    f"[^{string.ascii_lowercase}{string.ascii_uppercase}{string.digits}_]"
)
