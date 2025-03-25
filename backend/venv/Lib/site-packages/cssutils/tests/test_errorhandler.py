"""Tests for parsing which does not raise Exceptions normally"""

import io
import logging
import sys
import xml.dom

import pytest

import cssutils


@pytest.fixture(autouse=True)
def save_log(monkeypatch):
    """
    Replace default log and ignore its output.
    """
    monkeypatch.setattr(cssutils.log, 'raiseExceptions', False)
    monkeypatch.setattr(
        cssutils.log, '_log', logging.getLogger('IGNORED-CSSUTILS-TEST')
    )


class TestErrorHandler:
    def _setHandler(self):
        "sets new handler and returns StringIO instance to getvalue"
        s = io.StringIO()
        h = logging.StreamHandler(s)
        h.setFormatter(logging.Formatter('%(levelname)s    %(message)s'))
        # remove if present already
        cssutils.log.removeHandler(h)
        cssutils.log.addHandler(h)
        return s

    def test_calls(self):
        "cssutils.log.*"
        s = self._setHandler()
        cssutils.log.setLevel(logging.DEBUG)
        cssutils.log.debug('msg', neverraise=True)
        assert s.getvalue() == 'DEBUG    msg\n'

        s = self._setHandler()
        cssutils.log.setLevel(logging.INFO)
        cssutils.log.info('msg', neverraise=True)
        assert s.getvalue() == 'INFO    msg\n'

        s = self._setHandler()
        cssutils.log.setLevel(logging.WARNING)
        cssutils.log.warn('msg', neverraise=True)
        assert s.getvalue() == 'WARNING    msg\n'

        s = self._setHandler()
        cssutils.log.setLevel(logging.ERROR)
        cssutils.log.error('msg', neverraise=True)
        assert s.getvalue() == 'ERROR    msg\n'

        s = self._setHandler()
        cssutils.log.setLevel(logging.FATAL)
        cssutils.log.fatal('msg', neverraise=True)
        assert s.getvalue() == 'CRITICAL    msg\n'

        s = self._setHandler()
        cssutils.log.setLevel(logging.CRITICAL)
        cssutils.log.critical('msg', neverraise=True)
        assert s.getvalue() == 'CRITICAL    msg\n'

        s = self._setHandler()
        cssutils.log.setLevel(logging.CRITICAL)
        cssutils.log.error('msg', neverraise=True)
        assert s.getvalue() == ''

    def test_linecol(self):
        "cssutils.log line col"
        o = cssutils.log.raiseExceptions
        cssutils.log.raiseExceptions = True

        s = cssutils.css.CSSStyleSheet()
        try:
            s.cssText = '@import x;'
        except xml.dom.DOMException as e:
            assert str(e) == 'CSSImportRule: Unexpected ident. [1:9: x]'
            assert e.line == 1
            assert e.col == 9
            if sys.platform.startswith('java'):
                assert e.msg == 'CSSImportRule: Unexpected ident. [1:9: x]'
            else:
                assert e.args == ('CSSImportRule: Unexpected ident. [1:9: x]',)

        cssutils.log.raiseExceptions = o

    @pytest.mark.network
    def test_handlers(self):
        "cssutils.log"
        s = self._setHandler()

        cssutils.log.setLevel(logging.FATAL)
        assert cssutils.log.getEffectiveLevel() == logging.FATAL

        cssutils.parseString('a { color: 1 }')
        assert s.getvalue() == ''

        cssutils.log.setLevel(logging.DEBUG)
        cssutils.parseString('a { color: 1 }')
        # TODO: Fix?
        # self.assertEqual(
        #     s.getvalue(),
        #     u'ERROR    Property: Invalid value for "CSS Color Module '
        #     'Level 3/CSS Level 2.1" property: 1 [1:5: color]\n')
        assert (
            s.getvalue() == 'ERROR    Property: Invalid value for "CSS Level 2.1" '
            'property: 1 [1:5: color]\n'
        )

        s = self._setHandler()

        cssutils.log.setLevel(logging.ERROR)
        cssutils.parseUrl('http://example.com')
        assert s.getvalue()[:38] == 'ERROR    Expected "text/css" mime type'

    def test_parsevalidation(self):
        style = 'color: 1'
        t = 'a { %s }' % style

        cssutils.log.setLevel(logging.DEBUG)

        # sheet
        s = self._setHandler()
        cssutils.parseString(t)
        assert len(s.getvalue()) != 0

        s = self._setHandler()
        cssutils.parseString(t, validate=False)
        assert s.getvalue() == ''

        # style
        s = self._setHandler()
        cssutils.parseStyle(style)
        assert len(s.getvalue()) != 0

        s = self._setHandler()
        cssutils.parseStyle(style, validate=True)
        assert len(s.getvalue()) != 0

        s = self._setHandler()
        cssutils.parseStyle(style, validate=False)
        assert s.getvalue() == ''
