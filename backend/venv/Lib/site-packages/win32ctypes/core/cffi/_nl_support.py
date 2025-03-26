#
# (C) Copyright 2015-18 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from ._util import ffi, dlls

ffi.cdef("""

UINT WINAPI GetACP(void);

""")


def _GetACP():
    return dlls.kernel32.GetACP()
