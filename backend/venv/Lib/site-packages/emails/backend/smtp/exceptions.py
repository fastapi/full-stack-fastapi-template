# encoding: utf-8
from __future__ import unicode_literals
import socket


class SMTPConnectNetworkError(IOError):
    """Network error during connection establishment."""

    @classmethod
    def from_ioerror(cls, exc):
        o = cls()
        o.errno = exc.errno
        o.filename = exc.filename
        o.strerror = exc.strerror or str(exc)
        return o
