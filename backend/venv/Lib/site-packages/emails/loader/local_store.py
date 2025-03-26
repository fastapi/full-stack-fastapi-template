# encoding: utf-8
from __future__ import unicode_literals
from email.utils import parseaddr
import logging
import mimetypes

import os
from os import path
import errno
from zipfile import ZipFile
import email

from ..compat import to_unicode, string_types, to_native, formataddr as compat_formataddr

from ..loader.helpers import decode_text
from ..message import Message
from ..utils import decode_header

class FileNotFound(Exception):
    pass


def split_template_path(template):
    """Split a path into segments and perform a sanity check.  If it detects
    '..' in the path it will raise a `TemplateNotFound` error.
    """
    pieces = []
    for piece in template.split('/'):
        if path.sep in piece \
                or (path.altsep and path.altsep in piece) or \
                        piece == path.pardir:
            raise FileNotFound(template)
        elif piece and piece != '.':
            pieces.append(piece)
    return pieces


def open_if_exists(filename, mode='rb'):
    """Returns a file descriptor for the filename if that file exists,
    otherwise `None`.
    """
    try:
        return open(filename, mode)
    except IOError as e:
        if e.errno not in (errno.ENOENT, errno.EISDIR):
            raise


class BaseLoader(object):

    def __getitem__(self, filename):
        try:
            contents, _ = self.get_file(filename)
            return contents
        except FileNotFound:
            return None

    def get_file(self, name):
        raise NotImplementedError

    def list_files(self):
        raise NotImplementedError

    def content(self, filename, is_html=False, decode=True, guess_charset=False, charset='utf-8'):
        data = self[filename]
        if decode:
            data, encoding = decode_text(data,
                                         is_html=is_html,
                                         guess_charset=guess_charset,
                                         try_common_charsets=False,
                                         fallback_charset=charset)
        return data

    def find_index_file(self, filename=None, extensions=('.html', '.htm'), stop_names=('index', ), raise_if_not_found=True):

        if filename:
            if self[filename]:
                return filename
            else:
                raise FileNotFound(filename)

        found_files = []

        for filename in self.list_files():

            bn = os.path.basename(filename)
            if bn.startswith('.'):
                # ignore hidden files
                continue
            name, ext = os.path.splitext(bn)

            if ext in extensions:
                if stop_names and name in stop_names:
                    return filename
                found_files.append(filename)

        # Return first found file
        if found_files:
            return found_files[0]
        elif raise_if_not_found:
            raise FileNotFound('index %s' % "|".join(extensions))

    def find_index_html(self, filename=None):
        return self.find_index_file(filename=filename)

    def find_index_text(self, filename=None):
        return self.find_index_file(filename=filename,
                                    extensions=('.txt', ),
                                    stop_names=('index', ),
                                    raise_if_not_found=False)


# FileSystemLoader from jinja2.loaders

class FileSystemLoader(BaseLoader):
    """Loads templates from the file system.  This loader can find templates
    in folders on the file system and is the preferred way to load them.

    The loader takes the path to the templates as string, or if multiple
    locations are wanted a list of them which is then looked up in the
    given order:

    >>> loader = FileSystemLoader('/path/to/templates')
    >>> loader = FileSystemLoader(['/path/to/templates', '/other/path'])

    Per default the template encoding is ``'utf-8'`` which can be changed
    by setting the `encoding` parameter to something else.
    """

    def __init__(self, searchpath, encoding='utf-8', base_path=None):
        if isinstance(searchpath, string_types):
            searchpath = [searchpath]
        self.searchpath = list(searchpath)
        self.encoding = encoding
        self.base_path = base_path

    def get_file(self, filename):
        if self.base_path:
            filename = path.join(self.base_path, filename)
        pieces = split_template_path(filename)
        for searchpath in self.searchpath:
            filename = path.join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read()
            finally:
                f.close()
            return contents, filename
        raise FileNotFound(filename)

    def list_files(self):
        found = set()
        for searchpath in self.searchpath:
            for dirpath, dirnames, filenames in os.walk(searchpath):
                for filename in filenames:
                    template = path.join(dirpath, filename) \
                        [len(searchpath):].strip(path.sep) \
                        .replace(path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        yield template


class ZipLoader(BaseLoader):

    """
    Load files from zip file
    """

    common_filename_charsets = ['ascii', 'cp866', 'cp1251', 'utf-8']


    def __init__(self, file, encoding='utf-8', base_path=None):

        if not isinstance(file, ZipFile):
            file = ZipFile(file, 'r')

        self.zipfile = file
        self.encoding = encoding
        self.base_path = base_path
        self._decoded_filenames = None
        self._original_filenames = None

    def _decode_filename(self, name):
        for enc in self.common_filename_charsets:
            try:
                return to_unicode(name, enc)
            except UnicodeDecodeError:
                pass
        return name

    def _unpack(self):
        if self._decoded_filenames is None:
            self._original_filenames = set(self.zipfile.namelist())
            self._decoded_filenames = dict([(self._decode_filename(name), name) for name in self._original_filenames])

    def get_file(self, name):

        if self.base_path:
            name = path.join(self.base_path, name)

        name = path.join(*split_template_path(name))

        self._unpack()

        if isinstance(name, str):
            name = to_unicode(name, 'utf-8')

        if name not in self._original_filenames:
            name = self._decoded_filenames.get(name)

        if name is None:
            raise FileNotFound(name)

        return self.zipfile.read(name), name

    def list_files(self):
        self._unpack()
        return sorted(self._decoded_filenames)


class MsgLoader(BaseLoader):
    """
    Load files from email.Message
    """

    common_charsets = ['ascii', 'utf-8', 'utf-16', 'windows-1252', 'cp850', 'windows-1251']

    def __init__(self, msg, base_path=None):
        if isinstance(msg, string_types):
            self.msg = email.message_from_string(msg)
        elif isinstance(msg, bytes):
            self.msg = email.message_from_string(to_native(msg))
        else:
            self.msg = msg
        self.base_path = base_path
        self._html_parts = []
        self._text_parts = []
        self._files = {}
        self._content_ids = {}
        self._parsed = False
        self.headers = {}

    def decode_text(self, text, charset=None):
        if charset:
            try:
                return text.decode(charset), charset
            except UnicodeError:
                pass
        for charset in self.common_charsets:
            try:
                return text.decode(charset), charset
            except UnicodeError:
                pass
        return text, None

    def clean_content_id(self, content_id):
        if content_id.startswith('<'):
            content_id = content_id[1:]
        if content_id.endswith('>'):
            content_id = content_id[:-1]
        return content_id

    def extract_part_text(self, part):
        return self.decode_text(part.get_payload(decode=True), charset=part.get_param('charset'))[0]

    def add_html_part(self, part):
        self._html_parts.append({'data': self.extract_part_text(part),
                                 'content_type': part.get_content_type()})

    def add_text_part(self, part):
        self._text_parts.append({'data': self.extract_part_text(part),
                                 'content_type': part.get_content_type()})

    def add_attachment_part(self, part):
        counter = 1
        f = {}

        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            if not ext:
                # Use a generic bag-of-bits extension
                ext = '.bin'
            filename = 'part-%03d%s' % (counter, ext)
            counter += 1
        f['filename'] = filename
        f['content_type'] = part.get_content_type()

        content_id = part['Content-ID']
        if content_id:
            f['content_id'] = self.clean_content_id(content_id)
            f['inline'] = True
            self._content_ids[f['content_id']] = f['filename']
        f['data'] = part.get_payload(decode=True)
        self._files[f['filename']] = f

    def _parse(self):
        for part in self.msg.walk():
            content_type = part.get_content_type()

            if content_type.startswith('multipart/'):
                continue

            if content_type == 'text/html':
                self.add_html_part(part)
                continue

            if content_type == 'text/plain':
                self.add_text_part(part)
                continue

            self.add_attachment_part(part)

    def parse(self):
        if not self._parsed:
            self._parse()
        self._parsed = True

    def get_file(self, name):
        self.parse()
        if name.startswith('cid:'):
            name = self._content_ids.get(name[4:])
        f = self._files.get(name)
        if f:
            return f['data'], name
        raise FileNotFound(name)

    def list_files(self):
        self.parse()
        return self._files

    @property
    def attachments(self):
        self.parse()
        return self._files.values()

    @property
    def html(self):
        self.parse()
        return self._html_parts and self._html_parts[0]['data'] or None

    @property
    def text(self):
        self.parse()
        return self._text_parts and self._text_parts[0]['data'] or None

    def decode_header_value(self, v):
        if isinstance(v, bytes):
            v = self.decode_text(v)[0]
        return decode_header(v)

    def decode_address_header_value(self, value, skip_invalid=False):

        r = []

        if isinstance(value, bytes):
            value = self.decode_text(value)[0]

        for token in value.split(','):
            name, email = parseaddr(token.strip())
            if not name and '@' not in email:
                # invalid address header content - name without email
                if not skip_invalid:
                    r.append(decode_header(email))
            else:
                r.append(compat_formataddr([decode_header(name), email]))

        return r

    def filter_header(self, name):
        return name == 'subject' or name in Message.ADDRESS_HEADERS

    def copy_header_to_message(self, message, name, value):
        """
        Set header in email.Message

        :param message: message to set header to
        :param name: header name
        :param value: header value
        :return:
        """
        if name == 'subject':
            message.subject = self.decode_header_value(value)
        elif name == 'to':
            r = self.decode_address_header_value(value)
            if r:
                message.mail_to = r

        elif name == 'from':
            r = self.decode_address_header_value(value)
            if r:
                message.mail_from = r[0]
        elif name in Message.ADDRESS_HEADERS:
            message._headers[name] = ",".join(self.decode_address_header_value(value))
        else:
            message._headers[name] = self.decode_header_value(value)


    def copy_headers_to_message(self, message):
        """
        Decode headers from loaded email.Message object and copy them to emails.Message object

        :param message: emails.Message object to copy headers to
        :param headers: list of headers to parse. if None, parse 'Subject' header and all 'address headers'
        :return: None
        """
        for k, v in self.msg.items():
            k = k.lower()
            if self.filter_header(k):
                self.copy_header_to_message(message, k, v)


