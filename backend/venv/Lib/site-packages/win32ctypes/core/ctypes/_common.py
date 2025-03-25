#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import ctypes
import sys
from ctypes import (
    pythonapi, POINTER, c_void_p, py_object, c_char_p, c_int, c_long, c_int64,
    c_longlong)
from ctypes import cast  # noqa imported here for convenience
from ctypes.wintypes import BYTE

from ._util import function_factory

PPy_UNICODE = c_void_p
LPBYTE = POINTER(BYTE)
is_64bits = sys.maxsize > 2**32
Py_ssize_t = c_int64 if is_64bits else c_int

if ctypes.sizeof(c_long) == ctypes.sizeof(c_void_p):
    LONG_PTR = c_long
elif ctypes.sizeof(c_longlong) == ctypes.sizeof(c_void_p):
    LONG_PTR = c_longlong

_PyBytes_FromStringAndSize = function_factory(
    pythonapi.PyBytes_FromStringAndSize,
    [c_char_p, Py_ssize_t],
    return_type=py_object)


def IS_INTRESOURCE(x):
    return x >> 16 == 0


byreference = ctypes.byref


def dereference(x):
    return x.contents


class Libraries(object):

    def __getattr__(self, name):
        library = ctypes.WinDLL(name)
        self.__dict__[name] = library
        return library


dlls = Libraries()
