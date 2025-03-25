#
# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from ctypes.wintypes import UINT

from ._util import function_factory, dlls

_GetACP = function_factory(dlls.kernel32.GetACP, None, UINT)
