# encoding: utf-8
from __future__ import unicode_literals

import uuid
from mimetypes import guess_type
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from os.path import basename

from ..compat import urlparse, string_types, to_bytes
from ..utils import fetch_url, encode_header


MIMETYPE_UNKNOWN = 'application/unknown'


def fix_content_type(content_type, t='image'):
    if not content_type:
        return "%s/unknown" % t
    else:
        return content_type


class BaseFile(object):

    """
    Store base "attachment-file" information.
    """

    def __init__(self, **kwargs):
        """
        uri and filename are connected properties.
        if no filename set, filename extracted from uri.
        if no uri, but filename set, then uri==filename
        """
        self.uri = kwargs.get('uri', None)
        self.absolute_url = kwargs.get('absolute_url', None) or self.uri
        self.filename = kwargs.get('filename', None)
        self.data = kwargs.get('data', None)
        self._mime_type = kwargs.get('mime_type')
        self._headers = kwargs.get('headers', {})
        self._content_id = kwargs.get('content_id')
        self._content_disposition = kwargs.get('content_disposition', 'attachment')
        self.subtype = kwargs.get('subtype')
        self.local_loader = kwargs.get('local_loader')

    def as_dict(self, fields=None):
        fields = fields or ('uri', 'absolute_url', 'filename', 'data',
                            'mime_type', 'content_disposition', 'subtype')
        return dict([(k, getattr(self, k)) for k in fields])

    def get_data(self):
        _data = getattr(self, '_data', None)
        if isinstance(_data, string_types):
            return _data
        elif hasattr(_data, 'read'):
            return _data.read()
        else:
            return _data

    def set_data(self, value):
        self._data = value

    data = property(get_data, set_data)

    def get_uri(self):
        _uri = getattr(self, '_uri', None)
        if _uri is None:
            _filename = getattr(self, '_filename', None)
            if _filename:
                _uri = self._uri = _filename
        return _uri

    def set_uri(self, value):
        self._uri = value

    uri = property(get_uri, set_uri)

    def get_filename(self):
        _filename = getattr(self, '_filename', None)
        if _filename is None:
            _uri = getattr(self, '_uri', None)
            if _uri:
                parsed_path = urlparse.urlparse(_uri)
                _filename = basename(parsed_path.path)
                if not _filename:
                    _filename = str(uuid.uuid4())
                self._filename = _filename
        return _filename

    def set_filename(self, value):
        self._filename = value

    filename = property(get_filename, set_filename)

    def get_mime_type(self):
        r = getattr(self, '_mime_type', None)
        if r is None:
            filename = self.filename
            if filename:
                r = self._mime_type = guess_type(filename)[0]
        if not r:
            r = MIMETYPE_UNKNOWN
        self._mime_type = r
        return r

    mime_type = property(get_mime_type)

    def get_content_disposition(self):
        return getattr(self, '_content_disposition', None)

    def set_content_disposition(self, value):
        self._content_disposition = value

    content_disposition = property(get_content_disposition, set_content_disposition)

    @property
    def is_inline(self):
        return self.content_disposition == 'inline'

    @is_inline.setter
    def is_inline(self, value):
        if bool(value):
            self.content_disposition = 'inline'
        else:
            self.content_disposition = 'attachment'

    @property
    def content_id(self):
        if self._content_id is None:
            self._content_id = self.filename
        return self._content_id

    @property
    def mime(self):
        content_disposition = self.content_disposition
        if content_disposition is None:
            return None
        p = getattr(self, '_cached_part', None)
        if p is None:
            filename_header = encode_header(self.filename)
            p = MIMEBase(*self.mime_type.split('/', 1), name=filename_header)
            p.set_payload(to_bytes(self.data))
            encode_base64(p)
            if 'content-disposition' not in self._headers:
                p.add_header('Content-Disposition', self.content_disposition, filename=filename_header)
            if content_disposition == 'inline' and 'content-id' not in self._headers:
                p.add_header('Content-ID', '<%s>' % self.content_id)
            for (k, v) in self._headers.items():
                p.add_header(k, v)
            self._cached_part = p
        return p

    def reset_mime(self):
        self._mime = None

    def fetch(self):
        pass


class LazyHTTPFile(BaseFile):

    def __init__(self, requests_args=None, **kwargs):
        BaseFile.__init__(self, **kwargs)
        self.requests_args = requests_args
        self._fetched = False

    def fetch(self):
        if (not self._fetched) and self.uri:
            if self.local_loader:
                data = self.local_loader[self.uri]

                if data:
                    self._fetched = True
                    self._data = data
                    return

            r = fetch_url(url=self.absolute_url or self.uri, requests_args=self.requests_args)
            if r.status_code == 200:
                self._data = r.content
                self._headers = r.headers
                self._mime_type = fix_content_type(r.headers.get('content-type'), t='unknown')
                self._fetched = True

    def get_data(self):
        self.fetch()
        return self._data or ''

    def set_data(self, v):
        self._data = v

    data = property(get_data, set_data)

    @property
    def mime_type(self):
        self.fetch()
        return super(LazyHTTPFile, self).mime_type

    @property
    def headers(self):
        self.fetch()
        return self._headers
