# encoding: utf-8
from __future__ import unicode_literals
__all__ = ['guess_charset', 'fix_content_type']

import re
import cgi
import warnings

try:
    import charade as chardet
    warnings.warn("charade module is deprecated, update your requirements to chardet",
                  DeprecationWarning)
except ImportError:
    import chardet

from ..compat import to_native, to_unicode

# HTML page charset stuff

class ReRules:
    re_meta = b"(?i)(?<=<meta).*?(?=>)"
    re_is_http_equiv = b"http-equiv=\"?'?content-type\"?'?"
    re_parse_http_equiv = b"content=\"?'?([^\"'>]+)"
    re_charset = b"charset=\"?'?([\w-]+)\"?'?"

    def __init__(self, conv=None):
        if conv is None:
            conv = lambda x: x
        for k in dir(self):
            if k.startswith('re_'):
                setattr(self, k, re.compile(conv(getattr(self, k)), re.I + re.S + re.M))

RULES_U = ReRules(conv=to_unicode)
RULES_B = ReRules()


def guess_text_charset(text, is_html=False):
    if is_html:
        rules = isinstance(text, bytes) and RULES_B or RULES_U
        for meta in rules.re_meta.findall(text):
            if rules.re_is_http_equiv.findall(meta):
                for content in rules.re_parse_http_equiv.findall(meta):
                    for charset in rules.re_charset.findall(content):
                        return to_native(charset)
            else:
                for charset in rules.re_charset.findall(meta):
                    return to_native(charset)
    # guess by chardet
    if isinstance(text, bytes):
        return to_native(chardet.detect(text)['encoding'])


def guess_html_charset(html):
    return guess_text_charset(text=html, is_html=True)


def guess_charset(headers, html):

    # guess by http headers
    if headers:
        content_type = headers['content-type']
        if content_type:
            _, params = cgi.parse_header(content_type)
            r = params.get('charset', None)
            if r:
                return r

    # guess by html content
    charset = guess_html_charset(html)
    if charset:
        return to_unicode(charset)

COMMON_CHARSETS = ('ascii', 'utf-8', 'utf-16', 'windows-1251', 'windows-1252', 'cp850')

def decode_text(text,
                is_html=False,
                guess_charset=True,
                try_common_charsets=True,
                charsets=None,
                fallback_charset='utf-8'):

    if not isinstance(text, bytes):
        return text, None

    _charsets = []
    if guess_charset:
        c = guess_text_charset(text, is_html=is_html)
        if c:
            _charsets.append(c)

    if charsets:
        _charsets.extend(charsets)

    if try_common_charsets:
        _charsets.extend(COMMON_CHARSETS)

    if fallback_charset:
        _charsets.append(fallback_charset)

    _last_exc = None
    for enc in _charsets:
        try:
            return to_unicode(text, charset=enc), enc
        except UnicodeDecodeError as exc:
            _last_exc = exc

    raise _last_exc
