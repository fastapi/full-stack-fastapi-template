"""
libpq debugging tools

These functionalities are exposed here for convenience, but are not part of
the public interface and are subject to change at any moment.

Suggested usage::

    import logging
    import psycopg
    from psycopg import pq
    from psycopg.pq._debug import PGconnDebug

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("psycopg.debug")
    logger.setLevel(logging.INFO)

    assert pq.__impl__ == "python"
    pq.PGconn = PGconnDebug

    with psycopg.connect("") as conn:
        conn.pgconn.trace(2)
        conn.pgconn.set_trace_flags(
            pq.Trace.SUPPRESS_TIMESTAMPS | pq.Trace.REGRESS_MODE)
        ...

"""

# Copyright (C) 2022 The Psycopg Team

import inspect
import logging
from typing import Any, Callable
from functools import wraps

from . import PGconn, abc
from .misc import connection_summary
from .._compat import Self, TypeVar

Func = TypeVar("Func", bound=Callable[..., Any])

logger = logging.getLogger("psycopg.debug")


class PGconnDebug:
    """Wrapper for a PQconn logging all its access."""

    _pgconn: abc.PGconn

    def __init__(self, pgconn: abc.PGconn):
        super().__setattr__("_pgconn", pgconn)

    def __repr__(self) -> str:
        cls = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        info = connection_summary(self._pgconn)
        return f"<{cls} {info} at 0x{id(self):x}>"

    def __getattr__(self, attr: str) -> Any:
        value = getattr(self._pgconn, attr)
        if callable(value):
            return debugging(value)
        else:
            logger.info("PGconn.%s -> %s", attr, value)
            return value

    def __setattr__(self, attr: str, value: Any) -> None:
        setattr(self._pgconn, attr, value)
        logger.info("PGconn.%s <- %s", attr, value)

    @classmethod
    def connect(cls, conninfo: bytes) -> Self:
        return cls(debugging(PGconn.connect)(conninfo))

    @classmethod
    def connect_start(cls, conninfo: bytes) -> Self:
        return cls(debugging(PGconn.connect_start)(conninfo))

    @classmethod
    def ping(self, conninfo: bytes) -> int:
        return debugging(PGconn.ping)(conninfo)


def debugging(f: Func) -> Func:
    """Wrap a function in order to log its arguments and return value on call."""

    @wraps(f)
    def debugging_(*args: Any, **kwargs: Any) -> Any:
        reprs = []
        for arg in args:
            reprs.append(f"{arg!r}")
        for k, v in kwargs.items():
            reprs.append(f"{k}={v!r}")

        logger.info("PGconn.%s(%s)", f.__name__, ", ".join(reprs))
        try:
            rv = f(*args, **kwargs)
        except Exception as ex:
            logger.info("    <- %r", ex)
            raise
        else:
            # Display the return value only if the function is declared to return
            # something else than None.
            ra = inspect.signature(f).return_annotation
            if ra is not None or rv is not None:
                logger.info("    <- %r", rv)
            return rv

    return debugging_  # type: ignore
