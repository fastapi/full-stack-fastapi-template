"""
psycopg two-phase commit support
"""

# Copyright (C) 2021 The Psycopg Team

from __future__ import annotations

import re
import datetime as dt
from base64 import b64decode, b64encode
from dataclasses import dataclass, replace

_re_xid = re.compile(r"^(\d+)_([^_]*)_([^_]*)$")


@dataclass(frozen=True)
class Xid:
    """A two-phase commit transaction identifier.

    The object can also be unpacked as a 3-item tuple (`format_id`, `gtrid`,
    `bqual`).

    """

    format_id: int | None
    gtrid: str
    bqual: str | None
    prepared: dt.datetime | None = None
    owner: str | None = None
    database: str | None = None

    @classmethod
    def from_string(cls, s: str) -> Xid:
        """Try to parse an XA triple from the string.

        This may fail for several reasons. In such case return an unparsed Xid.
        """
        try:
            return cls._parse_string(s)
        except Exception:
            return Xid(None, s, None)

    def __str__(self) -> str:
        return self._as_tid()

    def __len__(self) -> int:
        return 3

    def __getitem__(self, index: int) -> int | str | None:
        return (self.format_id, self.gtrid, self.bqual)[index]

    @classmethod
    def _parse_string(cls, s: str) -> Xid:
        m = _re_xid.match(s)
        if not m:
            raise ValueError("bad Xid format")

        format_id = int(m.group(1))
        gtrid = b64decode(m.group(2)).decode()
        bqual = b64decode(m.group(3)).decode()
        return cls.from_parts(format_id, gtrid, bqual)

    @classmethod
    def from_parts(cls, format_id: int | None, gtrid: str, bqual: str | None) -> Xid:
        if format_id is not None:
            if bqual is None:
                raise TypeError("if format_id is specified, bqual must be too")
            if not 0 <= format_id < 0x80000000:
                raise ValueError("format_id must be a non-negative 32-bit integer")
            if len(bqual) > 64:
                raise ValueError("bqual must be not longer than 64 chars")
            if len(gtrid) > 64:
                raise ValueError("gtrid must be not longer than 64 chars")

        elif bqual is None:
            raise TypeError("if format_id is None, bqual must be None too")

        return Xid(format_id, gtrid, bqual)

    def _as_tid(self) -> str:
        """
        Return the PostgreSQL transaction_id for this XA xid.

        PostgreSQL wants just a string, while the DBAPI supports the XA
        standard and thus a triple. We use the same conversion algorithm
        implemented by JDBC in order to allow some form of interoperation.

        see also: the pgjdbc implementation
          http://cvs.pgfoundry.org/cgi-bin/cvsweb.cgi/jdbc/pgjdbc/org/
            postgresql/xa/RecoveredXid.java?rev=1.2
        """
        if self.format_id is None or self.bqual is None:
            # Unparsed xid: return the gtrid.
            return self.gtrid

        # XA xid: mash together the components.
        egtrid = b64encode(self.gtrid.encode()).decode()
        ebqual = b64encode(self.bqual.encode()).decode()

        return f"{self.format_id}_{egtrid}_{ebqual}"

    @classmethod
    def _get_recover_query(cls) -> str:
        return "SELECT gid, prepared, owner, database FROM pg_prepared_xacts"

    @classmethod
    def _from_record(
        cls, gid: str, prepared: dt.datetime, owner: str, database: str
    ) -> Xid:
        xid = Xid.from_string(gid)
        return replace(xid, prepared=prepared, owner=owner, database=database)


Xid.__module__ = "psycopg"
