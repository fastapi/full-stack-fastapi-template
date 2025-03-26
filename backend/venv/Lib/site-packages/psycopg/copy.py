"""
Module gathering the various parts of the copy subsystem.
"""

from typing import IO

from . import _copy, _copy_async
from .abc import Buffer

# re-exports

AsyncCopy = _copy_async.AsyncCopy
AsyncWriter = _copy_async.AsyncWriter
AsyncLibpqWriter = _copy_async.AsyncLibpqWriter
AsyncQueuedLibpqWriter = _copy_async.AsyncQueuedLibpqWriter

Copy = _copy.Copy
Writer = _copy.Writer
LibpqWriter = _copy.LibpqWriter
QueuedLibpqWriter = _copy.QueuedLibpqWriter


class FileWriter(Writer):
    """
    A `Writer` to write copy data to a file-like object.

    :param file: the file where to write copy data. It must be open for writing
        in binary mode.
    """

    def __init__(self, file: IO[bytes]):
        self.file = file

    def write(self, data: Buffer) -> None:
        self.file.write(data)
