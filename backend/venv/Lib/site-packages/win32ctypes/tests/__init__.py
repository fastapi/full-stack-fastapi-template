#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import os

if 'SHOW_TEST_ENV' in os.environ:
    import sys
    from win32ctypes.core import _backend
    is_64bits = sys.maxsize > 2**32
    print('=' * 30, file=sys.stderr)
    print(
        'Running on python: {} {}'.format(
            sys.version, '64bit' if is_64bits else '32bit'),
        file=sys.stderr)
    print('The executable is: {}'.format(sys.executable), file=sys.stderr)
    print('Using the {} backend'.format(_backend), file=sys.stderr)
    print('=' * 30, file=sys.stderr, flush=True)
