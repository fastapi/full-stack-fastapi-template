# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
pythoncompat
"""

from .orderedset import OrderedSet

#from . import _urlparse as urlparse


import sys

# -------
# Pythons
# -------

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)

#: Python 3.0.x
is_py30 = (is_py3 and _ver[1] == 0)

#: Python 3.1.x
is_py31 = (is_py3 and _ver[1] == 1)

#: Python 3.2.x
is_py32 = (is_py3 and _ver[1] == 2)

#: Python 3.3.x
is_py33 = (is_py3 and _ver[1] == 3)

#: Python 3.4.x
is_py34 = (is_py3 and _ver[1] == 4)
is_py34_plus = (is_py3 and _ver[1] >= 4)

#: Python 2.7.x
is_py27 = (is_py2 and _ver[1] == 7)

#: Python 2.6.x
is_py26 = (is_py2 and _ver[1] == 6)

#: Python 2.5.x
is_py25 = (is_py2 and _ver[1] == 5)

#: Python 2.4.x
is_py24 = (is_py2 and _ver[1] == 4)


# ---------
# Platforms
# ---------


# Syntax sugar.
_ver = sys.version.lower()

is_pypy = ('pypy' in _ver)
is_jython = ('jython' in _ver)
is_ironpython = ('iron' in _ver)

# Assume CPython, if nothing else.
is_cpython = not any((is_pypy, is_jython, is_ironpython))

# Windows-based system.
is_windows = 'win32' in str(sys.platform).lower()

# Standard Linux 2+ system.
is_linux = ('linux' in str(sys.platform).lower())
is_osx = ('darwin' in str(sys.platform).lower())
is_hpux = ('hpux' in str(sys.platform).lower())   # Complete guess.
is_solaris = ('solar==' in str(sys.platform).lower())   # Complete guess.

# ---------
# Specifics
# ---------

if is_py2:

    unichr = unichr
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)
    int_to_byte = chr

    import urlparse
    from .ordereddict import OrderedDict

    from StringIO import StringIO
    from cStringIO import StringIO as BytesIO
    NativeStringIO = BytesIO

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.encode(charset, errors)

    def is_callable(x):
        return callable(x)

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None:
            return None
        if isinstance(x, (bytes, bytearray, buffer)):
            return bytes(x)
        if isinstance(x, unicode):
            return x.encode(charset, errors)
        raise TypeError('Expected bytes')

    from email.utils import formataddr


elif is_py3:
    import urllib.parse as urlparse

    try:
        from collections.abc import Callable
    except ImportError:
        from collections import Callable

    from collections import OrderedDict

    from io import StringIO, BytesIO
    NativeStringIO = StringIO

    unichr = chr
    text_type = str
    string_types = (str, )
    integer_types = (int, )

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.decode(charset, errors)

    def is_callable(x):
        return isinstance(x, Callable)

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None:
            return None
        if isinstance(x, (bytes, bytearray, memoryview)):
            return bytes(x)
        if isinstance(x, str):
            return x.encode(charset, errors)
        raise TypeError('Expected bytes')

    from email.utils import escapesre, specialsre

    def formataddr(pair):
        """
        This code is copy of python2 email.utils.formataddr.
        Takes a 2-tuple of the form (realname, email_address) and returns RFC2822-like string.
        Does not encode non-ascii realname.

        Python3 email.utils.formataddr do encode realname.
        """
        name, address = pair
        if name:
            quotes = ''
            if specialsre.search(name):
                quotes = '"'
            name = escapesre.sub(r'\\\g<0>', name)
            return '%s%s%s <%s>' % (quotes, name, quotes, address)
        return address


def to_unicode(x, charset=sys.getdefaultencoding(), errors='strict',
               allow_none_charset=False):
    if x is None:
        return None
    if not isinstance(x, bytes):
        return text_type(x)
    if charset is None and allow_none_charset:
        return x
    return x.decode(charset, errors)