#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
""" A module which supports common Windows types. """
import contextlib
import collections
import time
from datetime import datetime as _datetime


class error(Exception):
    def __init__(self, *args, **kw):
        nargs = len(args)
        if nargs > 0:
            self.winerror = args[0]
        else:
            self.winerror = None
        if nargs > 1:
            self.funcname = args[1]
        else:
            self.funcname = None
        if nargs > 2:
            self.strerror = args[2]
        else:
            self.strerror = None
        Exception.__init__(self, *args, **kw)


@contextlib.contextmanager
def pywin32error():
    try:
        yield
    except WindowsError as exception:
        if not hasattr(exception, 'function'):
            exception.function = 'unknown'
        raise error(exception.winerror, exception.function, exception.strerror)


class datetime(_datetime):

    def Format(self, fmt='%c'):
        return self.strftime(fmt)


def Time(value):
    if isinstance(value, datetime):
        return value
    elif hasattr(value, 'timetuple'):
        timetuple = value.timetuple()
        return datetime.fromtimestamp(time.mktime(timetuple))
    elif isinstance(value, collections.abc.Sequence):
        time_value = time.mktime(value[:9])
        if len(value) == 10:
            time_value += value[9] / 1000.0
        return datetime.fromtimestamp(time_value)
    else:
        try:
            return datetime.fromtimestamp(value)
        except OSError as error:
            if error.errno == 22:
                raise ValueError(error.strerror)
            else:
                raise
