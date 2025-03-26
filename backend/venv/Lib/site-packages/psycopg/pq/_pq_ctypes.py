"""
libpq access using ctypes
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import sys
import ctypes
import ctypes.util
from ctypes import CFUNCTYPE, POINTER, Structure, c_char, c_char_p, c_int, c_size_t
from ctypes import c_ubyte, c_uint, c_void_p
from typing import Any, NoReturn

from .misc import find_libpq_full_path, version_pretty
from ..errors import NotSupportedError

libname = find_libpq_full_path()
if not libname:
    raise ImportError("libpq library not found")

pq = ctypes.cdll.LoadLibrary(libname)


class FILE(Structure):
    pass


FILE_ptr = POINTER(FILE)

if sys.platform == "linux":
    libcname = ctypes.util.find_library("c")
    if not libcname:
        # Likely this is a system using musl libc, see the following bug:
        # https://github.com/python/cpython/issues/65821
        libcname = "libc.so"
    libc = ctypes.cdll.LoadLibrary(libcname)

    fdopen = libc.fdopen
    fdopen.argtypes = (c_int, c_char_p)
    fdopen.restype = FILE_ptr


# Get the libpq version to define what functions are available.

PQlibVersion = pq.PQlibVersion
PQlibVersion.argtypes = []
PQlibVersion.restype = c_int

libpq_version = PQlibVersion()


# libpq data types


Oid = c_uint


class PGconn_struct(Structure):
    _fields_ = []


class PGresult_struct(Structure):
    _fields_ = []


class PQconninfoOption_struct(Structure):
    _fields_ = [
        ("keyword", c_char_p),
        ("envvar", c_char_p),
        ("compiled", c_char_p),
        ("val", c_char_p),
        ("label", c_char_p),
        ("dispchar", c_char_p),
        ("dispsize", c_int),
    ]


class PGnotify_struct(Structure):
    _fields_ = [
        ("relname", c_char_p),
        ("be_pid", c_int),
        ("extra", c_char_p),
    ]


class PGcancelConn_struct(Structure):
    _fields_ = []


class PGcancel_struct(Structure):
    _fields_ = []


class PGresAttDesc_struct(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("tableid", Oid),
        ("columnid", c_int),
        ("format", c_int),
        ("typid", Oid),
        ("typlen", c_int),
        ("atttypmod", c_int),
    ]


PGconn_ptr = POINTER(PGconn_struct)
PGresult_ptr = POINTER(PGresult_struct)
PQconninfoOption_ptr = POINTER(PQconninfoOption_struct)
PGnotify_ptr = POINTER(PGnotify_struct)
PGcancelConn_ptr = POINTER(PGcancelConn_struct)
PGcancel_ptr = POINTER(PGcancel_struct)
PGresAttDesc_ptr = POINTER(PGresAttDesc_struct)


# Function definitions as explained in PostgreSQL 12 documentation

# 33.1. Database Connection Control Functions

# PQconnectdbParams: doesn't seem useful, won't wrap for now

PQconnectdb = pq.PQconnectdb
PQconnectdb.argtypes = [c_char_p]
PQconnectdb.restype = PGconn_ptr

# PQsetdbLogin: not useful
# PQsetdb: not useful

# PQconnectStartParams: not useful

PQconnectStart = pq.PQconnectStart
PQconnectStart.argtypes = [c_char_p]
PQconnectStart.restype = PGconn_ptr

PQconnectPoll = pq.PQconnectPoll
PQconnectPoll.argtypes = [PGconn_ptr]
PQconnectPoll.restype = c_int

PQconndefaults = pq.PQconndefaults
PQconndefaults.argtypes = []
PQconndefaults.restype = PQconninfoOption_ptr

PQconninfoFree = pq.PQconninfoFree
PQconninfoFree.argtypes = [PQconninfoOption_ptr]
PQconninfoFree.restype = None

PQconninfo = pq.PQconninfo
PQconninfo.argtypes = [PGconn_ptr]
PQconninfo.restype = PQconninfoOption_ptr

PQconninfoParse = pq.PQconninfoParse
PQconninfoParse.argtypes = [c_char_p, POINTER(c_char_p)]
PQconninfoParse.restype = PQconninfoOption_ptr

PQfinish = pq.PQfinish
PQfinish.argtypes = [PGconn_ptr]
PQfinish.restype = None

PQreset = pq.PQreset
PQreset.argtypes = [PGconn_ptr]
PQreset.restype = None

PQresetStart = pq.PQresetStart
PQresetStart.argtypes = [PGconn_ptr]
PQresetStart.restype = c_int

PQresetPoll = pq.PQresetPoll
PQresetPoll.argtypes = [PGconn_ptr]
PQresetPoll.restype = c_int

PQping = pq.PQping
PQping.argtypes = [c_char_p]
PQping.restype = c_int


# 33.2. Connection Status Functions

PQdb = pq.PQdb
PQdb.argtypes = [PGconn_ptr]
PQdb.restype = c_char_p

PQuser = pq.PQuser
PQuser.argtypes = [PGconn_ptr]
PQuser.restype = c_char_p

PQpass = pq.PQpass
PQpass.argtypes = [PGconn_ptr]
PQpass.restype = c_char_p

PQhost = pq.PQhost
PQhost.argtypes = [PGconn_ptr]
PQhost.restype = c_char_p


def not_supported_before(fname: str, pgversion: int) -> Any:
    def not_supported(*args: Any, **kwargs: Any) -> NoReturn:
        raise NotSupportedError(
            f"{fname} requires libpq from PostgreSQL {version_pretty(pgversion)} on"
            f" the client; version {version_pretty(libpq_version)} available instead"
        )

    return not_supported


if libpq_version >= 120000:
    PQhostaddr = pq.PQhostaddr
    PQhostaddr.argtypes = [PGconn_ptr]
    PQhostaddr.restype = c_char_p
else:
    PQhostaddr = not_supported_before("PQhostaddr", 120000)

PQport = pq.PQport
PQport.argtypes = [PGconn_ptr]
PQport.restype = c_char_p

PQtty = pq.PQtty
PQtty.argtypes = [PGconn_ptr]
PQtty.restype = c_char_p

PQoptions = pq.PQoptions
PQoptions.argtypes = [PGconn_ptr]
PQoptions.restype = c_char_p

PQstatus = pq.PQstatus
PQstatus.argtypes = [PGconn_ptr]
PQstatus.restype = c_int

PQtransactionStatus = pq.PQtransactionStatus
PQtransactionStatus.argtypes = [PGconn_ptr]
PQtransactionStatus.restype = c_int

PQparameterStatus = pq.PQparameterStatus
PQparameterStatus.argtypes = [PGconn_ptr, c_char_p]
PQparameterStatus.restype = c_char_p

PQprotocolVersion = pq.PQprotocolVersion
PQprotocolVersion.argtypes = [PGconn_ptr]
PQprotocolVersion.restype = c_int

PQserverVersion = pq.PQserverVersion
PQserverVersion.argtypes = [PGconn_ptr]
PQserverVersion.restype = c_int

PQerrorMessage = pq.PQerrorMessage
PQerrorMessage.argtypes = [PGconn_ptr]
PQerrorMessage.restype = c_char_p

PQsocket = pq.PQsocket
PQsocket.argtypes = [PGconn_ptr]
PQsocket.restype = c_int

PQbackendPID = pq.PQbackendPID
PQbackendPID.argtypes = [PGconn_ptr]
PQbackendPID.restype = c_int

PQconnectionNeedsPassword = pq.PQconnectionNeedsPassword
PQconnectionNeedsPassword.argtypes = [PGconn_ptr]
PQconnectionNeedsPassword.restype = c_int

PQconnectionUsedPassword = pq.PQconnectionUsedPassword
PQconnectionUsedPassword.argtypes = [PGconn_ptr]
PQconnectionUsedPassword.restype = c_int

PQsslInUse = pq.PQsslInUse
PQsslInUse.argtypes = [PGconn_ptr]
PQsslInUse.restype = c_int

# TODO: PQsslAttribute, PQsslAttributeNames, PQsslStruct, PQgetssl


# 33.3. Command Execution Functions

PQexec = pq.PQexec
PQexec.argtypes = [PGconn_ptr, c_char_p]
PQexec.restype = PGresult_ptr

PQexecParams = pq.PQexecParams
PQexecParams.argtypes = [
    PGconn_ptr,
    c_char_p,
    c_int,
    POINTER(Oid),
    POINTER(c_char_p),
    POINTER(c_int),
    POINTER(c_int),
    c_int,
]
PQexecParams.restype = PGresult_ptr

PQprepare = pq.PQprepare
PQprepare.argtypes = [PGconn_ptr, c_char_p, c_char_p, c_int, POINTER(Oid)]
PQprepare.restype = PGresult_ptr

PQexecPrepared = pq.PQexecPrepared
PQexecPrepared.argtypes = [
    PGconn_ptr,
    c_char_p,
    c_int,
    POINTER(c_char_p),
    POINTER(c_int),
    POINTER(c_int),
    c_int,
]
PQexecPrepared.restype = PGresult_ptr

PQdescribePrepared = pq.PQdescribePrepared
PQdescribePrepared.argtypes = [PGconn_ptr, c_char_p]
PQdescribePrepared.restype = PGresult_ptr

PQdescribePortal = pq.PQdescribePortal
PQdescribePortal.argtypes = [PGconn_ptr, c_char_p]
PQdescribePortal.restype = PGresult_ptr

if libpq_version >= 170000:
    PQclosePrepared = pq.PQclosePrepared
    PQclosePrepared.argtypes = [PGconn_ptr, c_char_p]
    PQclosePrepared.restype = PGresult_ptr

    PQclosePortal = pq.PQclosePortal
    PQclosePortal.argtypes = [PGconn_ptr, c_char_p]
    PQclosePortal.restype = PGresult_ptr

else:
    PQclosePrepared = not_supported_before("PQclosePrepared", 170000)
    PQclosePortal = not_supported_before("PQclosePortal", 170000)

PQresultStatus = pq.PQresultStatus
PQresultStatus.argtypes = [PGresult_ptr]
PQresultStatus.restype = c_int

# PQresStatus: not needed, we have pretty enums

PQresultErrorMessage = pq.PQresultErrorMessage
PQresultErrorMessage.argtypes = [PGresult_ptr]
PQresultErrorMessage.restype = c_char_p

# TODO: PQresultVerboseErrorMessage

PQresultErrorField = pq.PQresultErrorField
PQresultErrorField.argtypes = [PGresult_ptr, c_int]
PQresultErrorField.restype = c_char_p

PQclear = pq.PQclear
PQclear.argtypes = [PGresult_ptr]
PQclear.restype = None


# 33.3.2. Retrieving Query Result Information

PQntuples = pq.PQntuples
PQntuples.argtypes = [PGresult_ptr]
PQntuples.restype = c_int

PQnfields = pq.PQnfields
PQnfields.argtypes = [PGresult_ptr]
PQnfields.restype = c_int

PQfname = pq.PQfname
PQfname.argtypes = [PGresult_ptr, c_int]
PQfname.restype = c_char_p

# PQfnumber: useless and hard to use

PQftable = pq.PQftable
PQftable.argtypes = [PGresult_ptr, c_int]
PQftable.restype = Oid

PQftablecol = pq.PQftablecol
PQftablecol.argtypes = [PGresult_ptr, c_int]
PQftablecol.restype = c_int

PQfformat = pq.PQfformat
PQfformat.argtypes = [PGresult_ptr, c_int]
PQfformat.restype = c_int

PQftype = pq.PQftype
PQftype.argtypes = [PGresult_ptr, c_int]
PQftype.restype = Oid

PQfmod = pq.PQfmod
PQfmod.argtypes = [PGresult_ptr, c_int]
PQfmod.restype = c_int

PQfsize = pq.PQfsize
PQfsize.argtypes = [PGresult_ptr, c_int]
PQfsize.restype = c_int

PQbinaryTuples = pq.PQbinaryTuples
PQbinaryTuples.argtypes = [PGresult_ptr]
PQbinaryTuples.restype = c_int

PQgetvalue = pq.PQgetvalue
PQgetvalue.argtypes = [PGresult_ptr, c_int, c_int]
PQgetvalue.restype = POINTER(c_char)  # not a null-terminated string

PQgetisnull = pq.PQgetisnull
PQgetisnull.argtypes = [PGresult_ptr, c_int, c_int]
PQgetisnull.restype = c_int

PQgetlength = pq.PQgetlength
PQgetlength.argtypes = [PGresult_ptr, c_int, c_int]
PQgetlength.restype = c_int

PQnparams = pq.PQnparams
PQnparams.argtypes = [PGresult_ptr]
PQnparams.restype = c_int

PQparamtype = pq.PQparamtype
PQparamtype.argtypes = [PGresult_ptr, c_int]
PQparamtype.restype = Oid

# PQprint: pretty useless

# 33.3.3. Retrieving Other Result Information

PQcmdStatus = pq.PQcmdStatus
PQcmdStatus.argtypes = [PGresult_ptr]
PQcmdStatus.restype = c_char_p

PQcmdTuples = pq.PQcmdTuples
PQcmdTuples.argtypes = [PGresult_ptr]
PQcmdTuples.restype = c_char_p

PQoidValue = pq.PQoidValue
PQoidValue.argtypes = [PGresult_ptr]
PQoidValue.restype = Oid


# 33.3.4. Escaping Strings for Inclusion in SQL Commands

PQescapeLiteral = pq.PQescapeLiteral
PQescapeLiteral.argtypes = [PGconn_ptr, c_char_p, c_size_t]
PQescapeLiteral.restype = POINTER(c_char)

PQescapeIdentifier = pq.PQescapeIdentifier
PQescapeIdentifier.argtypes = [PGconn_ptr, c_char_p, c_size_t]
PQescapeIdentifier.restype = POINTER(c_char)

PQescapeStringConn = pq.PQescapeStringConn
# TODO: raises "wrong type" error
# PQescapeStringConn.argtypes = [
#     PGconn_ptr, c_char_p, c_char_p, c_size_t, POINTER(c_int)
# ]
PQescapeStringConn.restype = c_size_t

PQescapeString = pq.PQescapeString
# TODO: raises "wrong type" error
# PQescapeString.argtypes = [c_char_p, c_char_p, c_size_t]
PQescapeString.restype = c_size_t

PQescapeByteaConn = pq.PQescapeByteaConn
PQescapeByteaConn.argtypes = [
    PGconn_ptr,
    POINTER(c_char),  # actually POINTER(c_ubyte) but this is easier
    c_size_t,
    POINTER(c_size_t),
]
PQescapeByteaConn.restype = POINTER(c_ubyte)

PQescapeBytea = pq.PQescapeBytea
PQescapeBytea.argtypes = [
    POINTER(c_char),  # actually POINTER(c_ubyte) but this is easier
    c_size_t,
    POINTER(c_size_t),
]
PQescapeBytea.restype = POINTER(c_ubyte)


PQunescapeBytea = pq.PQunescapeBytea
PQunescapeBytea.argtypes = [
    POINTER(c_char),  # actually POINTER(c_ubyte) but this is easier
    POINTER(c_size_t),
]
PQunescapeBytea.restype = POINTER(c_ubyte)


# 33.4. Asynchronous Command Processing

PQsendQuery = pq.PQsendQuery
PQsendQuery.argtypes = [PGconn_ptr, c_char_p]
PQsendQuery.restype = c_int

PQsendQueryParams = pq.PQsendQueryParams
PQsendQueryParams.argtypes = [
    PGconn_ptr,
    c_char_p,
    c_int,
    POINTER(Oid),
    POINTER(c_char_p),
    POINTER(c_int),
    POINTER(c_int),
    c_int,
]
PQsendQueryParams.restype = c_int

PQsendPrepare = pq.PQsendPrepare
PQsendPrepare.argtypes = [PGconn_ptr, c_char_p, c_char_p, c_int, POINTER(Oid)]
PQsendPrepare.restype = c_int

PQsendQueryPrepared = pq.PQsendQueryPrepared
PQsendQueryPrepared.argtypes = [
    PGconn_ptr,
    c_char_p,
    c_int,
    POINTER(c_char_p),
    POINTER(c_int),
    POINTER(c_int),
    c_int,
]
PQsendQueryPrepared.restype = c_int

PQsendDescribePrepared = pq.PQsendDescribePrepared
PQsendDescribePrepared.argtypes = [PGconn_ptr, c_char_p]
PQsendDescribePrepared.restype = c_int

PQsendDescribePortal = pq.PQsendDescribePortal
PQsendDescribePortal.argtypes = [PGconn_ptr, c_char_p]
PQsendDescribePortal.restype = c_int

if libpq_version >= 170000:
    PQsendClosePrepared = pq.PQsendClosePrepared
    PQsendClosePrepared.argtypes = [PGconn_ptr, c_char_p]
    PQsendClosePrepared.restype = c_int

    PQsendClosePortal = pq.PQsendClosePortal
    PQsendClosePortal.argtypes = [PGconn_ptr, c_char_p]
    PQsendClosePortal.restype = c_int

else:
    PQsendClosePrepared = not_supported_before("PQsendClosePrepared", 170000)
    PQsendClosePortal = not_supported_before("PQsendClosePortal", 170000)

PQgetResult = pq.PQgetResult
PQgetResult.argtypes = [PGconn_ptr]
PQgetResult.restype = PGresult_ptr

PQconsumeInput = pq.PQconsumeInput
PQconsumeInput.argtypes = [PGconn_ptr]
PQconsumeInput.restype = c_int

PQisBusy = pq.PQisBusy
PQisBusy.argtypes = [PGconn_ptr]
PQisBusy.restype = c_int

PQsetnonblocking = pq.PQsetnonblocking
PQsetnonblocking.argtypes = [PGconn_ptr, c_int]
PQsetnonblocking.restype = c_int

PQisnonblocking = pq.PQisnonblocking
PQisnonblocking.argtypes = [PGconn_ptr]
PQisnonblocking.restype = c_int

PQflush = pq.PQflush
PQflush.argtypes = [PGconn_ptr]
PQflush.restype = c_int


# 32.6. Retrieving Query Results in Chunks
PQsetSingleRowMode = pq.PQsetSingleRowMode
PQsetSingleRowMode.argtypes = [PGconn_ptr]
PQsetSingleRowMode.restype = c_int

if libpq_version >= 170000:
    PQsetChunkedRowsMode = pq.PQsetChunkedRowsMode
    PQsetChunkedRowsMode.argtypes = [PGconn_ptr, c_int]
    PQsetChunkedRowsMode.restype = c_int
else:
    PQsetChunkedRowsMode = not_supported_before("PQsetChunkedRowsMode", 170000)

# 33.6. Canceling Queries in Progress

if libpq_version >= 170000:
    PQcancelCreate = pq.PQcancelCreate
    PQcancelCreate.argtypes = [PGconn_ptr]
    PQcancelCreate.restype = PGcancelConn_ptr

    PQcancelStart = pq.PQcancelStart
    PQcancelStart.argtypes = [PGcancelConn_ptr]
    PQcancelStart.restype = c_int

    PQcancelBlocking = pq.PQcancelBlocking
    PQcancelBlocking.argtypes = [PGcancelConn_ptr]
    PQcancelBlocking.restype = c_int

    PQcancelPoll = pq.PQcancelPoll
    PQcancelPoll.argtypes = [PGcancelConn_ptr]
    PQcancelPoll.restype = c_int

    PQcancelStatus = pq.PQcancelStatus
    PQcancelStatus.argtypes = [PGcancelConn_ptr]
    PQcancelStatus.restype = c_int

    PQcancelSocket = pq.PQcancelSocket
    PQcancelSocket.argtypes = [PGcancelConn_ptr]
    PQcancelSocket.restype = c_int

    PQcancelErrorMessage = pq.PQcancelErrorMessage
    PQcancelErrorMessage.argtypes = [PGcancelConn_ptr]
    PQcancelErrorMessage.restype = c_char_p

    PQcancelReset = pq.PQcancelReset
    PQcancelReset.argtypes = [PGcancelConn_ptr]
    PQcancelReset.restype = None

    PQcancelFinish = pq.PQcancelFinish
    PQcancelFinish.argtypes = [PGcancelConn_ptr]
    PQcancelFinish.restype = None

else:
    PQcancelCreate = not_supported_before("PQcancelCreate", 170000)
    PQcancelStart = not_supported_before("PQcancelStart", 170000)
    PQcancelBlocking = not_supported_before("PQcancelBlocking", 170000)
    PQcancelPoll = not_supported_before("PQcancelPoll", 170000)
    PQcancelStatus = not_supported_before("PQcancelStatus", 170000)
    PQcancelSocket = not_supported_before("PQcancelSocket", 170000)
    PQcancelErrorMessage = not_supported_before("PQcancelErrorMessage", 170000)
    PQcancelReset = not_supported_before("PQcancelReset", 170000)
    PQcancelFinish = not_supported_before("PQcancelFinish", 170000)


PQgetCancel = pq.PQgetCancel
PQgetCancel.argtypes = [PGconn_ptr]
PQgetCancel.restype = PGcancel_ptr

PQfreeCancel = pq.PQfreeCancel
PQfreeCancel.argtypes = [PGcancel_ptr]
PQfreeCancel.restype = None

PQcancel = pq.PQcancel
# TODO: raises "wrong type" error
# PQcancel.argtypes = [PGcancel_ptr, POINTER(c_char), c_int]
PQcancel.restype = c_int


# 33.8. Asynchronous Notification

PQnotifies = pq.PQnotifies
PQnotifies.argtypes = [PGconn_ptr]
PQnotifies.restype = PGnotify_ptr


# 33.9. Functions Associated with the COPY Command

PQputCopyData = pq.PQputCopyData
PQputCopyData.argtypes = [PGconn_ptr, c_char_p, c_int]
PQputCopyData.restype = c_int

PQputCopyEnd = pq.PQputCopyEnd
PQputCopyEnd.argtypes = [PGconn_ptr, c_char_p]
PQputCopyEnd.restype = c_int

PQgetCopyData = pq.PQgetCopyData
PQgetCopyData.argtypes = [PGconn_ptr, POINTER(c_char_p), c_int]
PQgetCopyData.restype = c_int


# 33.10. Control Functions

PQtrace = pq.PQtrace
PQtrace.argtypes = [PGconn_ptr, FILE_ptr]
PQtrace.restype = None

if libpq_version >= 140000:
    PQsetTraceFlags = pq.PQsetTraceFlags
    PQsetTraceFlags.argtypes = [PGconn_ptr, c_int]
    PQsetTraceFlags.restype = None
else:
    PQsetTraceFlags = not_supported_before("PQsetTraceFlags", 140000)

PQuntrace = pq.PQuntrace
PQuntrace.argtypes = [PGconn_ptr]
PQuntrace.restype = None

# 33.11. Miscellaneous Functions

PQfreemem = pq.PQfreemem
PQfreemem.argtypes = [c_void_p]
PQfreemem.restype = None

if libpq_version >= 100000:
    PQencryptPasswordConn = pq.PQencryptPasswordConn
    PQencryptPasswordConn.argtypes = [
        PGconn_ptr,
        c_char_p,
        c_char_p,
        c_char_p,
    ]
    PQencryptPasswordConn.restype = POINTER(c_char)
else:
    PQencryptPasswordConn = not_supported_before("PQencryptPasswordConn", 100000)

if libpq_version >= 170000:
    PQchangePassword = pq.PQchangePassword
    PQchangePassword.argtypes = [
        PGconn_ptr,
        c_char_p,
        c_char_p,
    ]
    PQchangePassword.restype = PGresult_ptr
else:
    PQchangePassword = not_supported_before("PQchangePassword", 170000)

PQmakeEmptyPGresult = pq.PQmakeEmptyPGresult
PQmakeEmptyPGresult.argtypes = [PGconn_ptr, c_int]
PQmakeEmptyPGresult.restype = PGresult_ptr

PQsetResultAttrs = pq.PQsetResultAttrs
PQsetResultAttrs.argtypes = [PGresult_ptr, c_int, PGresAttDesc_ptr]
PQsetResultAttrs.restype = c_int


# 33.12. Notice Processing

PQnoticeReceiver = CFUNCTYPE(None, c_void_p, PGresult_ptr)

PQsetNoticeReceiver = pq.PQsetNoticeReceiver
PQsetNoticeReceiver.argtypes = [PGconn_ptr, PQnoticeReceiver, c_void_p]
PQsetNoticeReceiver.restype = PQnoticeReceiver

# 34.5 Pipeline Mode

if libpq_version >= 140000:
    PQpipelineStatus = pq.PQpipelineStatus
    PQpipelineStatus.argtypes = [PGconn_ptr]
    PQpipelineStatus.restype = c_int

    PQenterPipelineMode = pq.PQenterPipelineMode
    PQenterPipelineMode.argtypes = [PGconn_ptr]
    PQenterPipelineMode.restype = c_int

    PQexitPipelineMode = pq.PQexitPipelineMode
    PQexitPipelineMode.argtypes = [PGconn_ptr]
    PQexitPipelineMode.restype = c_int

    PQpipelineSync = pq.PQpipelineSync
    PQpipelineSync.argtypes = [PGconn_ptr]
    PQpipelineSync.restype = c_int

    PQsendFlushRequest = pq.PQsendFlushRequest
    PQsendFlushRequest.argtypes = [PGconn_ptr]
    PQsendFlushRequest.restype = c_int

else:
    PQpipelineStatus = not_supported_before("PQpipelineStatus", 140000)
    PQenterPipelineMode = not_supported_before("PQenterPipelineMode", 140000)
    PQexitPipelineMode = not_supported_before("PQexitPipelineMode", 140000)
    PQpipelineSync = not_supported_before("PQpipelineSync", 140000)
    PQsendFlushRequest = not_supported_before("PQsendFlushRequest", 140000)


# 33.18. SSL Support

PQinitOpenSSL = pq.PQinitOpenSSL
PQinitOpenSSL.argtypes = [c_int, c_int]
PQinitOpenSSL.restype = None


def generate_stub() -> None:
    import re
    from ctypes import _CFuncPtr  # type: ignore[attr-defined]

    def type2str(fname: str, narg: int | None, t: Any) -> str:
        if t is None:
            return "None"
        elif t is c_void_p:
            return "Any"
        elif t is c_int or t is c_uint or t is c_size_t:
            return "int"
        elif t is c_char_p or t.__name__ == "LP_c_char":
            if narg is not None:
                return "bytes"
            else:
                return "bytes | None"

        elif t.__name__ in (
            "LP_PGconn_struct",
            "LP_PGresult_struct",
            "LP_PGcancelConn_struct",
            "LP_PGcancel_struct",
        ):
            if narg is not None:
                return f"{t.__name__[3:]} | None"
            else:
                return str(t.__name__[3:])

        elif t.__name__ in ("LP_PQconninfoOption_struct",):
            return f"Sequence[{t.__name__[3:]}]"

        elif t.__name__ in (
            "LP_c_ubyte",
            "LP_c_char_p",
            "LP_c_int",
            "LP_c_uint",
            "LP_c_ulong",
            "LP_FILE",
        ):
            return f"_Pointer[{t.__name__[3:]}]"

        else:
            assert False, f"can't deal with {t} in {fname}"

    fn = __file__ + "i"
    with open(fn) as f:
        lines = f.read().splitlines()

    istart, iend = (
        i
        for i, line in enumerate(lines)
        if re.match(r"\s*#\s*autogenerated:\s+(start|end)", line)
    )

    known = {
        line[4:].split("(", 1)[0] for line in lines[:istart] if line.startswith("def ")
    }

    signatures = []

    for name, obj in globals().items():
        if name in known:
            continue
        if not isinstance(obj, _CFuncPtr):
            continue

        params = []
        for i, t in enumerate(obj.argtypes):
            params.append(f"arg{i + 1}: {type2str(name, i, t)}")

        resname = type2str(name, None, obj.restype)

        signatures.append(f"def {name}({', '.join(params)}) -> {resname}: ...")

    lines[istart + 1 : iend] = signatures

    with open(fn, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")


if __name__ == "__main__":
    generate_stub()
