#
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from weakref import WeakKeyDictionary

from ._util import ffi

_keep_alive = WeakKeyDictionary()


def _PyBytes_FromStringAndSize(pointer, size):
    buffer = ffi.buffer(pointer, size)
    return buffer[:]


def byreference(x):
    return ffi.new(ffi.getctype(ffi.typeof(x), '*'), x)


def dereference(x):
    return x[0]


def PDWORD(value=0):
    return ffi.new("DWORD *", value)
