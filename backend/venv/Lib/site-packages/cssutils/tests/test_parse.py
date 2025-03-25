"""Tests for parsing which does not raise Exceptions normally"""

import urllib.error
import xml.dom
from unittest import mock

import pytest

import cssutils


class TestCSSParser:
    def _make_fetcher(self, encoding, content):
        "make an URL fetcher with specified data"

        def fetcher(url):
            return encoding, content

        return fetcher

    def test_init(self):
        "CSSParser.__init__()"
        assert cssutils.log.raiseExceptions

        # also the default:
        cssutils.log.raiseExceptions = True

        # default non raising parser
        p = cssutils.CSSParser()
        s = p.parseString('$')
        assert s.cssText == b''

        # explicit raiseExceptions=False
        p = cssutils.CSSParser(raiseExceptions=False)
        s = p.parseString('$')
        assert s.cssText == b''

        # working with sheet does raise though!
        with pytest.raises(xml.dom.DOMException):
            s.__setattr__('cssText', '$')

        # ----

        # raiseExceptions=True
        p = cssutils.CSSParser(raiseExceptions=True)
        with pytest.raises(xml.dom.SyntaxErr):
            p.parseString('$')

        # working with a sheet does raise too
        s = cssutils.css.CSSStyleSheet()
        with pytest.raises(xml.dom.DOMException):
            s.__setattr__('cssText', '$')

        # RESET cssutils.log.raiseExceptions
        cssutils.log.raiseExceptions = False
        s = cssutils.css.CSSStyleSheet()
        # does not raise!
        s.__setattr__('cssText', '$')
        assert s.cssText == b''

    def test_parseComments(self):
        "cssutils.CSSParser(parseComments=False)"
        css = '/*1*/ a { color: /*2*/ red; }'

        p = cssutils.CSSParser(parseComments=False)
        assert p.parseString(css).cssText == b'a {\n    color: red\n    }'
        p = cssutils.CSSParser(parseComments=True)
        assert p.parseString(css).cssText == b'/*1*/\na {\n    color: /*2*/ red\n    }'

    def test_parseUrl(self):
        "CSSParser.parseUrl()"
        # parseUrl(self, href, encoding=None, media=None, title=None):
        parser = cssutils.CSSParser()
        m = mock.Mock()
        with mock.patch('cssutils.util._defaultFetcher', m):
            m.return_value = (None, '')
            sheet = parser.parseUrl(
                'http://example.com', media='tv,print', title='test'
            )

        assert sheet.href == 'http://example.com'
        assert sheet.encoding == 'utf-8'
        assert sheet.media.mediaText == 'tv, print'
        assert sheet.title == 'test'

        # URL and content tests
        tests = {
            # (url, content): isSheet, encoding, cssText
            ('', None): (False, None, None),
            ('1', None): (False, None, None),
            ('mailto:a@bb.cd', None): (False, None, None),
            ('http://cthedot.de/test.css', None): (False, None, None),
            ('http://cthedot.de/test.css', ''): (True, 'utf-8', ''),
            ('http://cthedot.de/test.css', 'a'): (True, 'utf-8', ''),
            ('http://cthedot.de/test.css', 'a {color: red}'): (
                True,
                'utf-8',
                'a {\n    color: red\n    }',
            ),
            ('http://cthedot.de/test.css', '@charset "ascii";a {color: red}'): (
                True,
                'ascii',
                '@charset "ascii";\na {\n    color: red\n    }',
            ),
        }
        override = 'iso-8859-1'
        overrideprefix = '@charset "iso-8859-1";'
        httpencoding = None

        for (url, content), (isSheet, expencoding, cssText) in list(tests.items()):
            parser.setFetcher(self._make_fetcher(httpencoding, content))
            sheet1 = parser.parseUrl(url)
            sheet2 = parser.parseUrl(url, encoding=override)
            if isSheet:
                assert sheet1.encoding == expencoding
                assert sheet1.cssText == cssText.encode()
                assert sheet2.encoding == override
                if sheet1.cssText and cssText.startswith('@charset'):
                    assert sheet2.cssText == (
                        cssText.replace('ascii', override).encode()
                    )
                elif sheet1.cssText:
                    assert sheet2.cssText == (overrideprefix + '\n' + cssText).encode()
                else:
                    assert sheet2.cssText == (overrideprefix + cssText).encode()
            else:
                assert sheet1 is None
                assert sheet2 is None

        parser.setFetcher(None)

        with pytest.raises(ValueError):
            parser.parseUrl('../not-valid-in-urllib')

    @pytest.mark.network
    def test_parseUrl_404(self):
        parser = cssutils.CSSParser()
        with pytest.raises(urllib.error.HTTPError):
            parser.parseUrl(
                'http://cthedot.de/not-present.css',
            )

    def test_parseString(self):
        "CSSParser.parseString()"
        tests = {
            # (byte) string, encoding: encoding, cssText
            ('/*a*/', None): ('utf-8', b'/*a*/'),
            ('/*a*/', 'ascii'): ('ascii', b'@charset "ascii";\n/*a*/'),
            # org
            # ('/*\xc3\xa4*/', None): (u'utf-8', u'/*\xc3\xa4*/'.encode('utf-8')),
            # ('/*\xc3\xa4*/', 'utf-8'): (u'utf-8',
            #  u'@charset "utf-8";\n/*\xc3\xa4*/'.encode('utf-8')),
            # new for 2.x and 3.x
            ('/*\xe4*/'.encode(), None): ('utf-8', '/*\xe4*/'.encode()),
            ('/*\xe4*/'.encode(), 'utf-8'): (
                'utf-8',
                '@charset "utf-8";\n/*\xe4*/'.encode(),
            ),
            ('@charset "ascii";/*a*/', None): (
                'ascii',
                b'@charset "ascii";\n/*a*/',
            ),
            ('@charset "utf-8";/*a*/', None): (
                'utf-8',
                b'@charset "utf-8";\n/*a*/',
            ),
            ('@charset "iso-8859-1";/*a*/', None): (
                'iso-8859-1',
                b'@charset "iso-8859-1";\n/*a*/',
            ),
            # unicode string, no encoding: encoding, cssText
            ('/*€*/', None): ('utf-8', '/*€*/'.encode()),
            ('@charset "iso-8859-1";/*ä*/', None): (
                'iso-8859-1',
                '@charset "iso-8859-1";\n/*ä*/'.encode('iso-8859-1'),
            ),
            ('@charset "utf-8";/*€*/', None): (
                'utf-8',
                '@charset "utf-8";\n/*€*/'.encode(),
            ),
            ('@charset "utf-16";/**/', None): (
                'utf-16',
                '@charset "utf-16";\n/**/'.encode('utf-16'),
            ),
            # unicode string, encoding utf-8: encoding, cssText
            ('/*€*/', 'utf-8'): ('utf-8', '@charset "utf-8";\n/*€*/'.encode()),
            ('@charset "iso-8859-1";/*ä*/', 'utf-8'): (
                'utf-8',
                '@charset "utf-8";\n/*ä*/'.encode(),
            ),
            ('@charset "utf-8";/*€*/', 'utf-8'): (
                'utf-8',
                '@charset "utf-8";\n/*€*/'.encode(),
            ),
            ('@charset "utf-16";/**/', 'utf-8'): (
                'utf-8',
                b'@charset "utf-8";\n/**/',
            ),
            # probably not what is wanted but does not raise:
            ('/*€*/', 'ascii'): (
                'ascii',
                b'@charset "ascii";\n/*\\20AC */',
            ),
            ('/*€*/', 'iso-8859-1'): (
                'iso-8859-1',
                b'@charset "iso-8859-1";\n/*\\20AC */',
            ),
        }
        for test in tests:
            css, encoding = test
            sheet = cssutils.parseString(css, encoding=encoding)
            encoding, cssText = tests[test]
            assert encoding == sheet.encoding
            assert cssText == sheet.cssText

        tests = [
            # encoded css, overiding encoding
            ('/*€*/'.encode('utf-16'), 'utf-8'),
            ('/*ä*/'.encode('iso-8859-1'), 'ascii'),
            ('/*€*/'.encode(), 'ascii'),
            (b'a', 'utf-16'),
        ]
        for test in tests:
            # self.assertEqual(None, cssutils.parseString(css, encoding=encoding))
            with pytest.raises(UnicodeDecodeError):
                cssutils.parseString(test[0], test[1])

    def test_validate(self):
        """CSSParser(validate)"""
        style = 'color: red'
        t = 'a { %s }' % style

        # helper
        s = cssutils.parseString(t)
        assert s.validating
        s = cssutils.parseString(t, validate=False)
        assert s.validating is False
        s = cssutils.parseString(t, validate=True)
        assert s.validating

        d = cssutils.parseStyle(style)
        assert d.validating
        d = cssutils.parseStyle(style, validate=True)
        assert d.validating
        d = cssutils.parseStyle(style, validate=False)
        assert d.validating is False

        # parser
        p = cssutils.CSSParser()
        s = p.parseString(t)
        assert s.validating
        s = p.parseString(t, validate=False)
        assert s.validating is False
        s = p.parseString(t, validate=True)
        assert s.validating
        d = p.parseStyle(style)
        assert d.validating

        p = cssutils.CSSParser(validate=True)
        s = p.parseString(t)
        assert s.validating
        s = p.parseString(t, validate=False)
        assert s.validating is False
        s = p.parseString(t, validate=True)
        assert s.validating
        d = p.parseStyle(style)
        assert d.validating

        p = cssutils.CSSParser(validate=False)
        s = p.parseString(t)
        assert s.validating is False
        s = p.parseString(t, validate=False)
        assert s.validating is False
        s = p.parseString(t, validate=True)
        assert s.validating
        d = p.parseStyle(style)
        assert d.validating is False

        # url
        p = cssutils.CSSParser(validate=False)
        p.setFetcher(self._make_fetcher('utf-8', t))
        u = 'url'
        s = p.parseUrl(u)
        assert s.validating is False
        s = p.parseUrl(u, validate=False)
        assert s.validating is False
        s = p.parseUrl(u, validate=True)
        assert s.validating

        # check if it raises see log test

    def test_fetcher(self):
        """CSSParser.fetcher

        order:
           0. explicity given encoding OVERRIDE (cssutils only)

           1. An HTTP "charset" parameter in a "Content-Type" field
              (or similar parameters in other protocols)
           2. BOM and/or @charset (see below)
           3. <link charset=""> or other metadata from the linking mechanism (if any)
           4. charset of referring style sheet or document (if any)
           5. Assume UTF-8
        """
        tests = {
            # css, encoding, (mimetype, encoding, importcss):
            #    encoding, importIndex, importEncoding, importText
            # 0/0 override/override => ASCII/ASCII
            (
                '@charset "utf-16"; @import "x";',
                'ASCII',
                ('iso-8859-1', '@charset "latin1";/*t*/'),
            ): ('ascii', 1, 'ascii', b'@charset "ascii";\n/*t*/'),
            # 1/1 not tested her but same as next
            # 2/1 @charset/HTTP => UTF-16/ISO-8859-1
            (
                '@charset "UTF-16"; @import "x";',
                None,
                ('ISO-8859-1', '@charset "latin1";/*t*/'),
            ): (
                'utf-16',
                1,
                'iso-8859-1',
                b'@charset "iso-8859-1";\n/*t*/',
            ),
            # 2/2 @charset/@charset => UTF-16/ISO-8859-1
            (
                '@charset "UTF-16"; @import "x";',
                None,
                (None, '@charset "ISO-8859-1";/*t*/'),
            ): (
                'utf-16',
                1,
                'iso-8859-1',
                b'@charset "iso-8859-1";\n/*t*/',
            ),
            # 2/4 @charset/referrer => ASCII/ASCII
            ('@charset "ASCII"; @import "x";', None, (None, '/*t*/')): (
                'ascii',
                1,
                'ascii',
                b'@charset "ascii";\n/*t*/',
            ),
            # 5/5 default/default or referrer
            ('@import "x";', None, (None, '/*t*/')): (
                'utf-8',
                0,
                'utf-8',
                b'/*t*/',
            ),
            # 0/0 override/override+unicode
            (
                '@charset "utf-16"; @import "x";',
                'ASCII',
                (None, '@charset "latin1";/*\u0287*/'),
            ): ('ascii', 1, 'ascii', b'@charset "ascii";\n/*\\287 */'),
            # 2/1 @charset/HTTP+unicode
            ('@charset "ascii"; @import "x";', None, ('iso-8859-1', '/*\u0287*/')): (
                'ascii',
                1,
                'iso-8859-1',
                b'@charset "iso-8859-1";\n/*\\287 */',
            ),
            # 2/4 @charset/referrer+unicode
            ('@charset "ascii"; @import "x";', None, (None, '/*\u0287*/')): (
                'ascii',
                1,
                'ascii',
                b'@charset "ascii";\n/*\\287 */',
            ),
            # 5/1 default/HTTP+unicode
            ('@import "x";', None, ('ascii', '/*\u0287*/')): (
                'utf-8',
                0,
                'ascii',
                b'@charset "ascii";\n/*\\287 */',
            ),
            # 5/5 default+unicode/default+unicode
            ('@import "x";', None, (None, '/*\u0287*/')): (
                'utf-8',
                0,
                'utf-8',
                '/*\u0287*/'.encode(),
            ),
        }
        parser = cssutils.CSSParser()
        for test in tests:
            css, encoding, fetchdata = test
            sheetencoding, importIndex, importEncoding, importText = tests[test]

            # use setFetcher
            parser.setFetcher(self._make_fetcher(*fetchdata))
            # use init
            parser2 = cssutils.CSSParser(fetcher=self._make_fetcher(*fetchdata))

            sheet = parser.parseString(css, encoding=encoding)
            sheet2 = parser2.parseString(css, encoding=encoding)

            # sheet
            assert sheet.encoding == sheetencoding
            assert sheet2.encoding == sheetencoding
            # imported sheet
            assert sheet.cssRules[importIndex].styleSheet.encoding == importEncoding
            assert sheet2.cssRules[importIndex].styleSheet.encoding == importEncoding
            assert sheet.cssRules[importIndex].styleSheet.cssText == importText
            assert sheet2.cssRules[importIndex].styleSheet.cssText == importText

    def test_roundtrip(self):
        "cssutils encodings"
        css1 = r'''@charset "utf-8";
/* ä */'''
        s = cssutils.parseString(css1)
        css2 = str(s.cssText, 'utf-8')
        assert css1 == css2

        s = cssutils.parseString(css2)
        s.cssRules[0].encoding = 'ascii'
        css3 = r'''@charset "ascii";
/* \E4  */'''
        assert css3 == str(s.cssText, 'utf-8')

    def test_escapes(self):
        "cssutils escapes"
        css = r'\43\x { \43\x: \43\x !import\41nt }'
        sheet = cssutils.parseString(css)
        assert (
            sheet.cssText
            == rb'''C\x {
    c\x: C\x !important
    }'''
        )

        css = r'\ x{\ x :\ x ;y:1} '
        sheet = cssutils.parseString(css)
        assert (
            sheet.cssText
            == rb'''\ x {
    \ x: \ x;
    y: 1
    }'''
        )

    def test_invalidstring(self):
        "cssutils.parseString(INVALID_STRING)"
        validfromhere = '@namespace "x";'
        csss = (
            '''@charset "ascii
                ;'''
            + validfromhere,
            '''@charset 'ascii
                ;'''
            + validfromhere,
            '''@namespace "y
                ;'''
            + validfromhere,
            '''@import "y
                ;'''
            + validfromhere,
            '''@import url('a
                );'''
            + validfromhere,
            '''@unknown "y
                ;'''
            + validfromhere,
        )
        for css in csss:
            s = cssutils.parseString(css)
            assert validfromhere.encode() == s.cssText

        csss = (
            '''a { font-family: "Courier
                ; }''',
            r'''a { content: "\"; }
                ''',
            r'''a { content: "\\\"; }
                ''',
        )
        for css in csss:
            assert b'' == cssutils.parseString(css).cssText

    def test_invalid(self):
        "cssutils.parseString(INVALID_CSS)"
        tests = {
            'a {color: blue}} a{color: red} a{color: green}': '''a {
    color: blue
    }
a {
    color: green
    }''',
            'p @here {color: red} p {color: green}': 'p {\n    color: green\n    }',
        }

        for css in tests:
            exp = tests[css]
            if exp is None:
                exp = css
            s = cssutils.parseString(css)
            assert exp.encode() == s.cssText

    def test_nesting(self):
        "cssutils.parseString nesting"
        # examples from csslist 27.11.2007
        tests = {
            '@1; div{color:green}': 'div {\n    color: green\n    }',
            '@1 []; div{color:green}': 'div {\n    color: green\n    }',
            '@1 [{}]; div { color:green; }': 'div {\n    color: green\n    }',
            '@media all { @ } div{color:green}': 'div {\n    color: green\n    }',
            # should this be u''?
            '@1 { [ } div{color:green}': '',
            # red was eaten:
            '@1 { [ } ] div{color:red}div{color:green}': 'div {\n    color: green\n    }',
        }
        for css, exp in list(tests.items()):
            assert exp.encode() == cssutils.parseString(css).cssText

    def test_specialcases(self):
        "cssutils.parseString(special_case)"
        tests = {
            '''
    a[title="a not s\
o very long title"] {/*...*/}''': '''a[title="a not so very long title"] {
    /*...*/
    }'''
        }
        for css in tests:
            exp = tests[css]
            if exp is None:
                exp = css
            s = cssutils.parseString(css)
            assert exp.encode() == s.cssText

    def test_iehack(self):
        "IEhack: $property (not since 0.9.5b3)"
        # $color is not color!
        css = 'a { color: green; $color: red; }'
        s = cssutils.parseString(css)

        p1 = s.cssRules[0].style.getProperty('color')
        assert 'color' == p1.name
        assert 'color' == p1.literalname
        assert '' == s.cssRules[0].style.getPropertyValue('$color')

        p2 = s.cssRules[0].style.getProperty('$color')
        assert p2 is None

        assert 'green' == s.cssRules[0].style.getPropertyValue('color')
        assert 'green' == s.cssRules[0].style.color

    def test_attributes(self):
        "cssutils.parseString(href, media)"
        s = cssutils.parseString(
            "a{}", href="file:foo.css", media="screen, projection, tv"
        )
        assert s.href == "file:foo.css"
        assert s.media.mediaText == "screen, projection, tv"

        s = cssutils.parseString(
            "a{}", href="file:foo.css", media=["screen", "projection", "tv"]
        )
        assert s.media.mediaText == "screen, projection, tv"
