# encoding: utf-8
from __future__ import unicode_literals
from os.path import splitext

from ..compat import OrderedDict, string_types
from .file import BaseFile


class FileStore(object):
    pass


class MemoryFileStore(FileStore):

    file_cls = BaseFile

    def __init__(self, file_cls=None):
        if file_cls:
            self.file_cls = file_cls
        self._files = OrderedDict()
        self._filenames = {}

    def __contains__(self, k):
        if isinstance(k, self.file_cls):
            return k.uri in self._files
        elif isinstance(k, string_types):
            return k in self._files
        else:
            return False

    def keys(self):
        return list(self._files.keys())

    def __len__(self):
        return len(self._files)

    def as_dict(self):
        for d in self._files.values():
            yield d.as_dict()

    def remove(self, uri):
        if isinstance(uri, self.file_cls):
            uri = uri.uri

        assert isinstance(uri, string_types)

        v = self[uri]
        if v:
            filename = v.filename
            if filename and (filename in self._filenames):
                del self._filenames[filename]
            del self._files[uri]

    def unique_filename(self, filename, uri=None):

        if filename in self._filenames:
            n = 1
            basefilename, ext = splitext(filename)

            while True:
                n += 1
                filename = "%s-%d%s" % (basefilename, n, ext)
                if filename not in self._filenames:
                    break
        else:
            self._filenames[filename] = uri

        return filename

    def add(self, value, replace=False):

        if isinstance(value, self.file_cls):
            uri = value.uri
        elif isinstance(value, dict):
            value = self.file_cls(**value)
            uri = value.uri
        else:
            raise ValueError("Unknown file type: %s" % type(value))

        if (uri not in self._files) or replace:
            self.remove(uri)
            value.filename = self.unique_filename(value.filename, uri=uri)
            self._files[uri] = value

        return value

    def by_uri(self, uri):
        return self._files.get(uri, None)

    def by_filename(self, filename):
        uri = self._filenames.get(filename)
        if uri:
            return self.by_uri(uri)

    def __getitem__(self, uri):
        return self.by_uri(uri) or self.by_filename(uri)

    def __iter__(self):
        for k in self._files:
            yield self._files[k]
