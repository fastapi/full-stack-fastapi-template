"""
Timezone utility functions.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import logging
from datetime import timezone, tzinfo

from .pq.abc import PGconn
from ._compat import ZoneInfo

logger = logging.getLogger("psycopg")

_timezones: dict[bytes | None, tzinfo] = {
    None: timezone.utc,
    b"UTC": timezone.utc,
}


def get_tzinfo(pgconn: PGconn | None) -> tzinfo:
    """Return the Python timezone info of the connection's timezone."""
    tzname = pgconn.parameter_status(b"TimeZone") if pgconn else None
    try:
        return _timezones[tzname]
    except KeyError:
        sname = tzname.decode() if tzname else "UTC"
        try:
            zi: tzinfo = ZoneInfo(sname)
        except (KeyError, OSError):
            logger.warning("unknown PostgreSQL timezone: %r; will use UTC", sname)
            zi = timezone.utc
        except Exception as ex:
            logger.warning(
                "error handling PostgreSQL timezone: %r; will use UTC (%s - %s)",
                sname,
                type(ex).__name__,
                ex,
            )
            zi = timezone.utc

        _timezones[tzname] = zi
        return zi
