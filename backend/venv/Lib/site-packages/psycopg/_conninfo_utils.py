"""
Internal utilities to manipulate connection strings
"""

# Copyright (C) 2024 The Psycopg Team

from __future__ import annotations

import os
from functools import lru_cache
from ipaddress import ip_address
from dataclasses import dataclass

from . import errors as e
from . import pq
from .abc import ConnDict, ConnMapping


def split_attempts(params: ConnMapping) -> list[ConnDict]:
    """
    Split connection parameters with a sequence of hosts into separate attempts.
    """

    def split_val(key: str) -> list[str]:
        val = get_param(params, key)
        return val.split(",") if val else []

    hosts = split_val("host")
    hostaddrs = split_val("hostaddr")
    ports = split_val("port")

    if hosts and hostaddrs and len(hosts) != len(hostaddrs):
        raise e.OperationalError(
            f"could not match {len(hosts)} host names"
            f" with {len(hostaddrs)} hostaddr values"
        )

    nhosts = max(len(hosts), len(hostaddrs))

    if 1 < len(ports) != nhosts:
        raise e.OperationalError(
            f"could not match {len(ports)} port numbers to {len(hosts)} hosts"
        )

    # A single attempt to make. Don't mangle the conninfo string.
    if nhosts <= 1:
        return [{**params}]

    if len(ports) == 1:
        ports *= nhosts

    # Now all lists are either empty or have the same length
    rv = []
    for i in range(nhosts):
        attempt = {**params}
        if hosts:
            attempt["host"] = hosts[i]
        if hostaddrs:
            attempt["hostaddr"] = hostaddrs[i]
        if ports:
            attempt["port"] = ports[i]
        rv.append(attempt)

    return rv


def get_param(params: ConnMapping, name: str) -> str | None:
    """
    Return a value from a connection string.

    The value may be also specified in a PG* env var.
    """
    if name in params:
        return str(params[name])

    # TODO: check if in service

    paramdef = get_param_def(name)
    if not paramdef:
        return None

    env = os.environ.get(paramdef.envvar)
    if env is not None:
        return env

    return None


@dataclass
class ParamDef:
    """
    Information about defaults and env vars for connection params
    """

    keyword: str
    envvar: str
    compiled: str | None


def get_param_def(keyword: str, _cache: dict[str, ParamDef] = {}) -> ParamDef | None:
    """
    Return the ParamDef of a connection string parameter.
    """
    if not _cache:
        defs = pq.Conninfo.get_defaults()
        for d in defs:
            cd = ParamDef(
                keyword=d.keyword.decode(),
                envvar=d.envvar.decode() if d.envvar else "",
                compiled=d.compiled.decode() if d.compiled is not None else None,
            )
            _cache[cd.keyword] = cd

    return _cache.get(keyword)


@lru_cache
def is_ip_address(s: str) -> bool:
    """Return True if the string represent a valid ip address."""
    try:
        ip_address(s)
    except ValueError:
        return False
    return True
