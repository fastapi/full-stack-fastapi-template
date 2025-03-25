#
# (C) Copyright 2017 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import warnings
from win32ctypes.pywin32.pywintypes import *  # noqa

warnings.warn(
    "Please use 'from win32ctypes.pywin32 import pywintypes'",
    DeprecationWarning)
