#
# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from ctypes.wintypes import BOOL, DWORD, HANDLE, HMODULE, LPCWSTR

from ._util import check_null, check_false, function_factory, dlls

_LoadLibraryEx = function_factory(
    dlls.kernel32.LoadLibraryExW,
    [LPCWSTR, HANDLE, DWORD],
    HMODULE, check_null)

_FreeLibrary = function_factory(
    dlls.kernel32.FreeLibrary,
    [HMODULE],
    BOOL,
    check_false)
