# encoding: utf-8
from __future__ import unicode_literals
import os
import socket
from time import mktime
from datetime import datetime
from random import randrange
from functools import wraps

import email.charset
from email import generator
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header, decode_header as decode_header_
from email.utils import formataddr, parseaddr, formatdate

import requests

from . import USER_AGENT
from .compat import string_types, to_unicode, NativeStringIO, is_py2, BytesIO, to_native
from .exc import HTTPLoaderError


_charsets_loaded = False

CHARSETS_FIX = [
    ['windows-1251', 'QP', 'QP'],
    # koi8 should by send as Quoted Printable because of bad SpamAssassin reaction on base64 (2008)
    ['koi8-r', 'QP', 'QP'],
    ['utf-8', 'BASE64', 'BASE64']
]


def load_email_charsets():
    global _charsets_loaded
    if not _charsets_loaded:
        for (charset, header_enc, body_enc) in CHARSETS_FIX:
            email.charset.add_charset(charset,
                                      getattr(email.charset, header_enc),
                                      getattr(email.charset, body_enc),
                                      charset)


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


# Django's CachedDnsName:
# Cached the hostname, but do it lazily: socket.getfqdn() can take a couple of
# seconds, which slows down the restart of the server.
class CachedDnsName(object):
    def __str__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        if not hasattr(self, '_fqdn'):
            self._fqdn = socket.getfqdn()
        return self._fqdn


DNS_NAME = CachedDnsName()


def decode_header(value, default="utf-8", errors='strict'):
    """Decode the specified header value"""
    value = to_native(value, charset=default, errors=errors)
    return "".join([to_unicode(text, charset or default, errors) for text, charset in decode_header_(value)])


class MessageID:
    """Returns a string suitable for RFC 2822 compliant Message-ID, e.g:
    <20020201195627.33539.96671@nightshade.la.mastaler.com>
    Optional idstring if given is a string used to strengthen the
    uniqueness of the message id.
    Based on django.core.mail.message.make_msgid
    """

    def __init__(self, domain=None, idstring=None):
        self.domain = str(domain or DNS_NAME)
        try:
            pid = os.getpid()
        except AttributeError:
            # No getpid() in Jython.
            pid = 1
        self.idstring = ".".join([str(idstring or randrange(10000)), str(pid)])

    def __call__(self):
        r = ".".join([datetime.now().strftime("%Y%m%d%H%M%S.%f"),
                      str(randrange(100000)),
                      self.idstring])
        return "".join(['<', r, '@', self.domain, '>'])


def parse_name_and_email_list(elements, encoding='utf-8'):
    """
    Parse a list of address-like elements, i.e.:
     * "name <email>"
     * "email"
     * (name, email)

    :param elements: one element or list of elements
    :param encoding: element encoding, if bytes
    :return: list of pairs (name, email)
    """
    if not elements:
        return []

    if isinstance(elements, string_types):
        return [parse_name_and_email(elements, encoding), ]

    if not isinstance(elements, (list, tuple)):
        raise TypeError("Can not parse_name_and_email_list from %s" % elements.__repr__())

    if len(elements) == 2:
        # Oops, it may be pair (name, email) or pair of emails [email1, email2]
        # Let's do some guesses
        if isinstance(elements, tuple):
            n, e = elements
            if isinstance(e, string_types) and (not n or isinstance(e, string_types)):
                # It is probably a pair (name, email)
                return [parse_name_and_email(elements, encoding), ]

    return [parse_name_and_email(x, encoding) for x in elements]


def parse_name_and_email(obj, encoding='utf-8'):
    # In:  'john@smith.me' or  '"John Smith" <john@smith.me>' or ('John Smith', 'john@smith.me')
    # Out: (u'John Smith', u'john@smith.me')

    if isinstance(obj, (list, tuple)):
        if len(obj) == 2:
            name, email = obj
        else:
            raise ValueError("Can not parse_name_and_email from %s" % obj)
    elif isinstance(obj, string_types):
        name, email = parseaddr(obj)
    else:
        raise ValueError("Can not parse_name_and_email from %s" % obj)

    return to_unicode(name, encoding) or None, to_unicode(email, encoding) or None


def sanitize_email(addr, encoding='ascii', parse=False):
    if parse:
        _, addr = parseaddr(to_unicode(addr))
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if '@' in addr:
            localpart, domain = addr.split('@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna').decode('ascii')
            addr = '@'.join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return addr


def sanitize_address(addr, encoding='ascii'):
    if isinstance(addr, string_types):
        addr = parseaddr(to_unicode(addr))
    nm, addr = addr
    # This try-except clause is needed on Python 3 < 3.2.4
    # http://bugs.python.org/issue14291
    try:
        nm = Header(nm, encoding).encode()
    except UnicodeEncodeError:
        nm = Header(nm, 'utf-8').encode()
    return formataddr((nm, sanitize_email(addr, encoding=encoding, parse=False)))


class MIMEMixin():
    def as_string(self, unixfrom=False, linesep='\n'):
        """Return the entire formatted message as a string.
        Optional `unixfrom' when True, means include the Unix From_ envelope
        header.
        This overrides the default as_string() implementation to not mangle
        lines that begin with 'From '. See bug #13433 for details.
        """
        fp = NativeStringIO()
        g = generator.Generator(fp, mangle_from_=False)
        if is_py2:
            g.flatten(self, unixfrom=unixfrom)
        else:
            g.flatten(self, unixfrom=unixfrom, linesep=linesep)

        return fp.getvalue()

    if is_py2:
        as_bytes = as_string
    else:
        def as_bytes(self, unixfrom=False, linesep='\n'):
            """Return the entire formatted message as bytes.
            Optional `unixfrom' when True, means include the Unix From_ envelope
            header.
            This overrides the default as_bytes() implementation to not mangle
            lines that begin with 'From '. See bug #13433 for details.
            """
            fp = BytesIO()
            g = generator.BytesGenerator(fp, mangle_from_=False)
            g.flatten(self, unixfrom=unixfrom, linesep=linesep)
            return fp.getvalue()


class SafeMIMEText(MIMEMixin, MIMEText):
    def __init__(self, text, subtype, charset):
        self.encoding = charset
        MIMEText.__init__(self, text, subtype, charset)


class SafeMIMEMultipart(MIMEMixin, MIMEMultipart):
    def __init__(self, _subtype='mixed', boundary=None, _subparts=None, encoding=None, **_params):
        self.encoding = encoding
        MIMEMultipart.__init__(self, _subtype, boundary, _subparts, **_params)


DEFAULT_REQUESTS_PARAMS = dict(allow_redirects=True,
                             verify=False, timeout=10,
                             headers={'User-Agent': USER_AGENT})


def fetch_url(url, valid_http_codes=(200, ), requests_args=None):
    args = {}
    args.update(DEFAULT_REQUESTS_PARAMS)
    args.update(requests_args or {})
    r = requests.get(url, **args)
    if valid_http_codes and (r.status_code not in valid_http_codes):
        raise HTTPLoaderError('Error loading url: %s. HTTP status: %s' % (url, r.status_code))
    return r


def encode_header(value, charset='utf-8'):
    if isinstance(value, string_types):
        value = to_unicode(value, charset=charset).rstrip()
        _r = Header(value, charset)
        return str(_r)
    else:
        return value


def renderable(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        r = f(self, *args, **kwargs)
        render = getattr(r, 'render', None)
        if render:
            d = render(**(self.render_data or {}))
            return d
        else:
            return r

    return wrapper


def format_date_header(v, localtime=True):
    if isinstance(v, datetime):
        return formatdate(mktime(v.timetuple()), localtime)
    elif isinstance(v, float):
        # probably timestamp
        return formatdate(v, localtime)
    elif v is None:
        return formatdate(None, localtime)
    else:
        return v
