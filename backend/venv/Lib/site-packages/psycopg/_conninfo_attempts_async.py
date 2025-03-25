"""
Separate connection attempts from a connection string.
"""

# Copyright (C) 2024 The Psycopg Team

from __future__ import annotations

import socket
import logging
from random import shuffle

from . import errors as e
from .abc import ConnDict, ConnMapping
from ._conninfo_utils import get_param, get_param_def, is_ip_address, split_attempts

if True:  # ASYNC:
    import asyncio

logger = logging.getLogger("psycopg")


async def conninfo_attempts_async(params: ConnMapping) -> list[ConnDict]:
    """Split a set of connection params on the single attempts to perform.

    A connection param can perform more than one attempt more than one ``host``
    is provided.

    Also perform async resolution of the hostname into hostaddr. Because a host
    can resolve to more than one address, this can lead to yield more attempts
    too. Raise `OperationalError` if no host could be resolved.

    Because the libpq async function doesn't honour the timeout, we need to
    reimplement the repeated attempts.
    """
    last_exc = None
    attempts = []
    if prefer_standby := get_param(params, "target_session_attrs") == "prefer-standby":
        params = {k: v for k, v in params.items() if k != "target_session_attrs"}

    for attempt in split_attempts(params):
        try:
            attempts.extend(await _resolve_hostnames(attempt))
        except OSError as ex:
            logger.debug("failed to resolve host %r: %s", attempt.get("host"), ex)
            last_exc = ex

    if not attempts:
        assert last_exc
        # We couldn't resolve anything
        raise e.OperationalError(str(last_exc))

    if get_param(params, "load_balance_hosts") == "random":
        shuffle(attempts)

    # Order matters: first try all the load-balanced host in standby mode,
    # then allow primary
    if prefer_standby:
        attempts = [
            {**a, "target_session_attrs": "standby"} for a in attempts
        ] + attempts

    return attempts


async def _resolve_hostnames(params: ConnDict) -> list[ConnDict]:
    """
    Perform async DNS lookup of the hosts and return a list of connection attempts.

    If a ``host`` param is present but not ``hostname``, resolve the host
    addresses asynchronously.

    :param params: The input parameters, for instance as returned by
        `~psycopg.conninfo.conninfo_to_dict()`. The function expects at most
        a single entry for host, hostaddr because it is designed to further
        process the input of split_attempts().

    :return: A list of attempts to make (to include the case of a hostname
        resolving to more than one IP).
    """
    host = get_param(params, "host")
    if not host or host.startswith("/") or host[1:2] == ":":
        # Local path, or no host to resolve
        return [params]

    hostaddr = get_param(params, "hostaddr")
    if hostaddr:
        # Already resolved
        return [params]

    if is_ip_address(host):
        # If the host is already an ip address don't try to resolve it
        return [{**params, "hostaddr": host}]

    port = get_param(params, "port")
    if not port:
        port_def = get_param_def("port")
        port = port_def and port_def.compiled or "5432"

    if True:  # ASYNC:
        loop = asyncio.get_running_loop()
        ans = await loop.getaddrinfo(
            host, port, proto=socket.IPPROTO_TCP, type=socket.SOCK_STREAM
        )
    else:
        ans = socket.getaddrinfo(
            host, port, proto=socket.IPPROTO_TCP, type=socket.SOCK_STREAM
        )

    return [{**params, "hostaddr": item[4][0]} for item in ans]
