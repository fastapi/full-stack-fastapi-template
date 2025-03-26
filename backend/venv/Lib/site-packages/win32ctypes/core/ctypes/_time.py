#
# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from ctypes.wintypes import DWORD

from ._util import function_factory, dlls


_GetTickCount = function_factory(
    dlls.kernel32.GetTickCount,
    None, DWORD)
