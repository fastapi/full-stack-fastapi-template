#
# (C) Copyright 2015-18 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from ._util import ffi, dlls

ffi.cdef("""

DWORD WINAPI GetTickCount(void);

""")


def _GetTickCount():
    return dlls.kernel32.GetTickCount()
