"""
Functions to manipulate conninfo strings
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import re

from . import _conninfo_attempts, _conninfo_attempts_async, _conninfo_utils
from . import errors as e
from . import pq
from .abc import ConnDict, ConnParam

# re-exoprts
conninfo_attempts = _conninfo_attempts.conninfo_attempts
conninfo_attempts_async = _conninfo_attempts_async.conninfo_attempts_async

# Default timeout for connection a attempt.
# Arbitrary timeout, what applied by the libpq on my computer.
# Your mileage won't vary.
_DEFAULT_CONNECT_TIMEOUT = 130


def make_conninfo(conninfo: str = "", **kwargs: ConnParam) -> str:
    """
    Merge a string and keyword params into a single conninfo string.

    :param conninfo: A `connection string`__ as accepted by PostgreSQL.
    :param kwargs: Parameters overriding the ones specified in `!conninfo`.
    :return: A connection string valid for PostgreSQL, with the `!kwargs`
        parameters merged.

    Raise `~psycopg.ProgrammingError` if the input doesn't make a valid
    conninfo string.

    .. __: https://www.postgresql.org/docs/current/libpq-connect.html
           #LIBPQ-CONNSTRING
    """
    if not conninfo and not kwargs:
        return ""

    # If no kwarg specified don't mung the conninfo but check if it's correct.
    # Make sure to return a string, not a subtype, to avoid making Liskov sad.
    if not kwargs:
        _parse_conninfo(conninfo)
        return str(conninfo)

    # Override the conninfo with the parameters
    # Drop the None arguments
    kwargs = {k: v for (k, v) in kwargs.items() if v is not None}

    if conninfo:
        tmp = conninfo_to_dict(conninfo)
        tmp.update(kwargs)
        kwargs = tmp

    conninfo = " ".join(f"{k}={_param_escape(str(v))}" for (k, v) in kwargs.items())

    # Verify the result is valid
    _parse_conninfo(conninfo)

    return conninfo


def conninfo_to_dict(conninfo: str = "", **kwargs: ConnParam) -> ConnDict:
    """
    Convert the `!conninfo` string into a dictionary of parameters.

    :param conninfo: A `connection string`__ as accepted by PostgreSQL.
    :param kwargs: Parameters overriding the ones specified in `!conninfo`.
    :return: Dictionary with the parameters parsed from `!conninfo` and
        `!kwargs`.

    Raise `~psycopg.ProgrammingError` if `!conninfo` is not a a valid connection
    string.

    .. __: https://www.postgresql.org/docs/current/libpq-connect.html
           #LIBPQ-CONNSTRING
    """
    opts = _parse_conninfo(conninfo)
    rv: ConnDict = {
        opt.keyword.decode(): opt.val.decode() for opt in opts if opt.val is not None
    }
    for k, v in kwargs.items():
        if v is not None:
            rv[k] = v
    return rv


def _parse_conninfo(conninfo: str) -> list[pq.ConninfoOption]:
    """
    Verify that `!conninfo` is a valid connection string.

    Raise ProgrammingError if the string is not valid.

    Return the result of pq.Conninfo.parse() on success.
    """
    try:
        return pq.Conninfo.parse(conninfo.encode())
    except e.OperationalError as ex:
        raise e.ProgrammingError(str(ex)) from None


re_escape = re.compile(r"([\\'])")
re_space = re.compile(r"\s")


def _param_escape(s: str) -> str:
    """
    Apply the escaping rule required by PQconnectdb
    """
    if not s:
        return "''"

    s = re_escape.sub(r"\\\1", s)
    if re_space.search(s):
        s = "'" + s + "'"

    return s


def timeout_from_conninfo(params: ConnDict) -> int:
    """
    Return the timeout in seconds from the connection parameters.
    """
    # Follow the libpq convention:
    #
    # - 0 or less means no timeout (but we will use a default to simulate
    #   the socket timeout)
    # - at least 2 seconds.
    #
    # See connectDBComplete in fe-connect.c
    value: str | int | None = _conninfo_utils.get_param(params, "connect_timeout")
    if value is None:
        value = _DEFAULT_CONNECT_TIMEOUT
    try:
        timeout = int(float(value))
    except ValueError:
        raise e.ProgrammingError(f"bad value for connect_timeout: {value!r}") from None

    if timeout <= 0:
        # The sync connect function will stop on the default socket timeout
        # Because in async connection mode we need to enforce the timeout
        # ourselves, we need a finite value.
        timeout = _DEFAULT_CONNECT_TIMEOUT
    elif timeout < 2:
        # Enforce a 2s min
        timeout = 2

    return timeout
