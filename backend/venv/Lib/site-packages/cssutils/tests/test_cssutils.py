"""Testcases for cssutils.css.CSSCharsetRule"""

import codecs
import os
import sys
import tempfile
from unittest import mock

import pytest

import cssutils

from . import basetest


@pytest.fixture
def serializer(monkeypatch):
    monkeypatch.setattr(cssutils, 'ser', cssutils.serialize.CSSSerializer())


class TestCSSutils(basetest.BaseTestCase):
    exp = '''@import "import/import2.css";
.import {
    /* ./import.css */
    background-image: url(images/example.gif)
    }'''

    def test_parseString(self):
        "cssutils.parseString()"
        s = cssutils.parseString(
            self.exp, media='handheld, screen', title='from string'
        )
        assert isinstance(s, cssutils.css.CSSStyleSheet)
        assert s.href is None
        assert self.exp.encode() == s.cssText
        assert 'utf-8' == s.encoding
        assert 'handheld, screen' == s.media.mediaText
        assert 'from string' == s.title
        assert self.exp.encode() == s.cssText

        ir = s.cssRules[0]
        assert 'import/import2.css' == ir.href
        irs = ir.styleSheet
        assert isinstance(irs, cssutils.css.CSSStyleSheet)

        href = basetest.get_sheet_filename('import.css')
        href = cssutils.helper.path2url(href)
        s = cssutils.parseString(self.exp, href=href)
        assert href == s.href

        ir = s.cssRules[0]
        assert 'import/import2.css' == ir.href
        irs = ir.styleSheet
        assert isinstance(irs, cssutils.css.CSSStyleSheet)
        assert (
            irs.cssText == b'@import "../import3.css";\n'
            b'@import "import-impossible.css" print;\n.import2 {\n'
            b'    /* sheets/import2.css */\n'
            b'    background: url(http://example.com/images/example.gif);\n'
            b'    background: url(//example.com/images/example.gif);\n'
            b'    background: url(/images/example.gif);\n'
            b'    background: url(images2/example.gif);\n'
            b'    background: url(./images2/example.gif);\n'
            b'    background: url(../images/example.gif);\n'
            b'    background: url(./../images/example.gif)\n'
            b'    }'
        )

        tests = {
            'a {color: red}': 'a {\n    color: red\n    }',
            'a {color: rgb(1,2,3)}': 'a {\n    color: rgb(1, 2, 3)\n    }',
        }
        self.do_equal_p(tests)

    def test_parseFile(self, monkeypatch):
        "cssutils.parseFile()"
        # name if used with open, href used for @import resolving
        name = basetest.get_sheet_filename('import.css')
        href = cssutils.helper.path2url(name)

        s = cssutils.parseFile(name, href=href, media='screen', title='from file')
        assert isinstance(s, cssutils.css.CSSStyleSheet)
        if sys.platform.startswith('java'):
            # on Jython only file:
            assert s.href.startswith('file:')
        else:
            # normally file:/// on win and file:/ on unix
            assert s.href.startswith('file:/')
        assert s.href.endswith('/sheets/import.css')
        assert 'utf-8' == s.encoding
        assert 'screen' == s.media.mediaText
        assert 'from file' == s.title
        assert self.exp.encode() == s.cssText

        ir = s.cssRules[0]
        assert 'import/import2.css' == ir.href
        irs = ir.styleSheet
        assert isinstance(irs, cssutils.css.CSSStyleSheet)
        assert (
            irs.cssText == b'@import "../import3.css";\n'
            b'@import "import-impossible.css" print;\n'
            b'.import2 {\n'
            b'    /* sheets/import2.css */\n'
            b'    background: url(http://example.com/images/example.gif);\n'
            b'    background: url(//example.com/images/example.gif);\n'
            b'    background: url(/images/example.gif);\n'
            b'    background: url(images2/example.gif);\n'
            b'    background: url(./images2/example.gif);\n'
            b'    background: url(../images/example.gif);\n'
            b'    background: url(./../images/example.gif)\n'
            b'    }'
        )

        # name is used for open and setting of href automatically
        # test needs to be relative to this test file!
        monkeypatch.chdir(os.path.dirname(__file__))
        name = basetest.get_sheet_filename('import.css')

        s = cssutils.parseFile(name, media='screen', title='from file')
        assert isinstance(s, cssutils.css.CSSStyleSheet)
        if sys.platform.startswith('java'):
            # on Jython only file:
            assert s.href.startswith('file:')
        else:
            # normally file:/// on win and file:/ on unix
            assert s.href.startswith('file:/')
        assert s.href.endswith('/sheets/import.css')
        assert 'utf-8' == s.encoding
        assert 'screen' == s.media.mediaText
        assert 'from file' == s.title
        assert self.exp.encode() == s.cssText

        ir = s.cssRules[0]
        assert 'import/import2.css' == ir.href
        irs = ir.styleSheet
        assert isinstance(irs, cssutils.css.CSSStyleSheet)
        assert (
            irs.cssText == b'@import "../import3.css";\n'
            b'@import "import-impossible.css" print;\n'
            b'.import2 {\n'
            b'    /* sheets/import2.css */\n'
            b'    background: url(http://example.com/images/example.gif);\n'
            b'    background: url(//example.com/images/example.gif);\n'
            b'    background: url(/images/example.gif);\n'
            b'    background: url(images2/example.gif);\n'
            b'    background: url(./images2/example.gif);\n'
            b'    background: url(../images/example.gif);\n'
            b'    background: url(./../images/example.gif)\n'
            b'    }'
        )

        # next test
        css = 'a:after { content: "羊蹄€\u2020" }'

        fd, name = tempfile.mkstemp('_cssutilstest.css')
        t = os.fdopen(fd, 'wb')
        t.write(css.encode('utf-8'))
        t.close()

        with pytest.raises(UnicodeDecodeError):
            cssutils.parseFile(name, 'ascii')

        # ???
        s = cssutils.parseFile(name, encoding='iso-8859-1')
        assert isinstance(s, cssutils.css.CSSStyleSheet)
        assert s.cssRules[1].selectorText == 'a:after'

        s = cssutils.parseFile(name, encoding='utf-8')
        assert isinstance(s, cssutils.css.CSSStyleSheet)
        assert s.cssRules[1].selectorText == 'a:after'

        css = '@charset "iso-8859-1"; a:after { content: "ä" }'
        t = codecs.open(name, 'w', 'iso-8859-1')
        t.write(css)
        t.close()

        with pytest.raises(UnicodeDecodeError):
            cssutils.parseFile(name, 'ascii')

        s = cssutils.parseFile(name, encoding='iso-8859-1')
        assert isinstance(s, cssutils.css.CSSStyleSheet)
        assert s.cssRules[1].selectorText == 'a:after'

        with pytest.raises(UnicodeDecodeError):
            cssutils.parseFile(name, 'utf-8')

        # clean up
        try:
            os.remove(name)
        except OSError:
            pass

    def test_parseUrl(self):
        "cssutils.parseUrl()"
        href = basetest.get_sheet_filename('import.css')
        # href = u'file:' + urllib.pathname2url(href)
        href = cssutils.helper.path2url(href)
        # href = 'http://seewhatever.de/sheets/import.css'
        s = cssutils.parseUrl(href, media='tv, print', title='from url')
        assert isinstance(s, cssutils.css.CSSStyleSheet)
        assert href == s.href
        assert self.exp.encode() == s.cssText
        assert 'utf-8' == s.encoding
        assert 'tv, print' == s.media.mediaText
        assert 'from url' == s.title

        sr = s.cssRules[1]
        img = sr.style.getProperty('background-image').propertyValue[0].value
        assert img == 'images/example.gif'

        ir = s.cssRules[0]
        assert 'import/import2.css' == ir.href
        irs = ir.styleSheet
        assert (
            irs.cssText == b'@import "../import3.css";\n'
            b'@import "import-impossible.css" print;\n'
            b'.import2 {\n'
            b'    /* sheets/import2.css */\n'
            b'    background: url(http://example.com/images/example.gif);\n'
            b'    background: url(//example.com/images/example.gif);\n'
            b'    background: url(/images/example.gif);\n'
            b'    background: url(images2/example.gif);\n'
            b'    background: url(./images2/example.gif);\n'
            b'    background: url(../images/example.gif);\n'
            b'    background: url(./../images/example.gif)\n'
            b'    }'
        )

        ir2 = irs.cssRules[0]
        assert '../import3.css' == ir2.href
        irs2 = ir2.styleSheet
        assert (
            irs2.cssText == b'/* import3 */\n'
            b'.import3 {\n'
            b'    /* from ./import/../import3.css */\n'
            b'    background: url(images/example3.gif);\n'
            b'    background: url(./images/example3.gif);\n'
            b'    background: url(import/images2/example2.gif);\n'
            b'    background: url(./import/images2/example2.gif);\n'
            b'    background: url(import/images2/../../images/example3.gif)\n'
            b'    }'
        )

    def test_setCSSSerializer(self):
        "cssutils.setSerializer() and cssutils.ser"
        s = cssutils.parseString('a { left: 0 }')
        exp4 = '''a {
    left: 0
    }'''
        exp1 = '''a {
 left: 0
 }'''
        assert exp4.encode() == s.cssText
        newser = cssutils.CSSSerializer(cssutils.serialize.Preferences(indent=' '))
        cssutils.setSerializer(newser)
        assert exp1.encode() == s.cssText
        newser = cssutils.CSSSerializer(cssutils.serialize.Preferences(indent='    '))
        cssutils.ser = newser
        assert exp4.encode() == s.cssText

    def test_parseStyle(self):
        "cssutils.parseStyle()"
        s = cssutils.parseStyle('x:0; y:red')
        assert isinstance(s, cssutils.css.CSSStyleDeclaration)
        assert s.cssText == 'x: 0;\ny: red'

        s = cssutils.parseStyle('@import "x";')
        assert isinstance(s, cssutils.css.CSSStyleDeclaration)
        assert s.cssText == ''

        tests = [('content: "ä"', 'iso-8859-1'), ('content: "€"', 'utf-8')]
        for v, e in tests:
            s = cssutils.parseStyle(v.encode(e), encoding=e)
            assert s.cssText == v

        with pytest.raises(UnicodeDecodeError):
            cssutils.parseStyle(
                'content: "ä"'.encode(),
                'ascii',
            )

    def test_getUrls(self):
        "cssutils.getUrls()"
        cssutils.ser.prefs.keepAllProperties = True

        css = r'''
        @import "im1";
        @import url(im2);
        @import url( im3 );
        @import url( "im4" );
        @import url( 'im5' );
        a {
            background-image: url(a) !important;
            background-\image: url(b);
            background: url(c) no-repeat !important;
            /* issue #46 */
            src: local("xx"),
                 url("f.woff") format("woff"),
                 url("f.otf") format("opentype"),
                 url("f.svg#f") format("svg");
            }'''
        urls = set(cssutils.getUrls(cssutils.parseString(css)))
        assert urls == {
            "im1",
            "im2",
            "im3",
            "im4",
            "im5",
            "a",
            "b",
            "c",
            'f.woff',
            'f.svg#f',
            'f.otf',
        }
        cssutils.ser.prefs.keepAllProperties = False

    def test_replaceUrls(self):
        "cssutils.replaceUrls()"
        cssutils.ser.prefs.keepAllProperties = True

        css = r'''
        @import "im1";
        @import url(im2);
        a {
            background-image: url(c) !important;
            background-\image: url(b);
            background: url(a) no-repeat !important;
            }'''
        s = cssutils.parseString(css)
        cssutils.replaceUrls(s, lambda old: "NEW" + old)
        assert '@import "NEWim1";' == s.cssRules[0].cssText
        assert 'NEWim2' == s.cssRules[1].href
        assert (
            '''background-image: url(NEWc) !important;
background-\\image: url(NEWb);
background: url(NEWa) no-repeat !important'''
            == s.cssRules[2].style.cssText
        )

        cssutils.ser.prefs.keepAllProperties = False

        # CSSStyleDeclaration
        style = cssutils.parseStyle(
            '''color: red;
                                        background-image:
                                            url(1.png),
                                            url('2.png')'''
        )
        cssutils.replaceUrls(style, lambda url: 'prefix/' + url)
        assert (
            style.cssText
            == '''color: red;
background-image: url(prefix/1.png), url(prefix/2.png)'''
        )

    @pytest.mark.usefixtures('serializer')
    def test_resolveImports(self):
        "cssutils.resolveImports(sheet)"
        cssutils.ser.prefs.useMinified()

        a = '@charset "iso-8859-1";@import"b.css";\xe4{color:green}'.encode(
            'iso-8859-1'
        )
        b = b'@charset "ascii";\\E4 {color:red}'

        # normal
        m = mock.Mock()
        with mock.patch('cssutils.util._defaultFetcher', m):
            m.return_value = (None, b)
            s = cssutils.parseString(a)

            # py3 TODO
            assert a == s.cssText
            assert b == s.cssRules[1].styleSheet.cssText

            c = cssutils.resolveImports(s)

            # py3 TODO
            assert b'\xc3\xa4{color:red}\xc3\xa4{color:green}' == c.cssText

            c.encoding = 'ascii'
            assert rb'@charset "ascii";\E4 {color:red}\E4 {color:green}' == c.cssText

        # b cannot be found
        m = mock.Mock()
        with mock.patch('cssutils.util._defaultFetcher', m):
            m.return_value = (None, None)
            s = cssutils.parseString(a)

            # py3 TODO
            assert a == s.cssText
            assert isinstance(s.cssRules[1].styleSheet, cssutils.css.CSSStyleSheet)
            c = cssutils.resolveImports(s)
            # py3 TODO
            assert b'@import"b.css";\xc3\xa4{color:green}' == c.cssText

        # @import with media
        a = '@import"b.css";@import"b.css" print, tv ;@import"b.css" all;'
        b = 'a {color: red}'
        m = mock.Mock()
        with mock.patch('cssutils.util._defaultFetcher', m):
            m.return_value = (None, b)
            s = cssutils.parseString(a)

            c = cssutils.resolveImports(s)

            assert b'a{color:red}@media print,tv{a{color:red}}a{color:red}' == c.cssText

        # cannot resolve with media => keep original
        a = '@import"b.css"print;'
        b = '@namespace "http://example.com";'
        m = mock.Mock()
        with mock.patch('cssutils.util._defaultFetcher', m):
            m.return_value = (None, b)
            s = cssutils.parseString(a)
            c = cssutils.resolveImports(s)
            assert a.encode() == c.cssText

        # urls are adjusted too, layout:
        # a.css
        # c.css
        # img/img.gif
        # b/
        #     b.css
        #     subimg/subimg.gif
        a = '''
             @import"b/b.css";
             a {
                 x: url(/img/abs.gif);
                 y: url(img/img.gif);
                 z: url(b/subimg/subimg.gif);
                 }'''

        def fetcher(url):
            c = {
                'b.css': '''
                     @import"../c.css";
                     b {
                         x: url(/img/abs.gif);
                         y: url(../img/img.gif);
                         z: url(subimg/subimg.gif);
                         }''',
                'c.css': '''
                     c {
                         x: url(/img/abs.gif);
                         y: url(./img/img.gif);
                         z: url(./b/subimg/subimg.gif);
                         }''',
            }
            return 'utf-8', c[os.path.split(url)[1]]

        @mock.patch.object(cssutils.util, '_defaultFetcher', new=fetcher)
        def do():
            s = cssutils.parseString(a)
            r = cssutils.resolveImports(s)
            return s, r

        s, r = do()

        cssutils.ser.prefs.useDefaults()
        cssutils.ser.prefs.keepComments = False
        expected = b'''c {
    x: url(/img/abs.gif);
    y: url(img/img.gif);
    z: url(b/subimg/subimg.gif)
    }
b {
    x: url(/img/abs.gif);
    y: url(img/img.gif);
    z: url(b/subimg/subimg.gif)
    }
a {
    x: url(/img/abs.gif);
    y: url(img/img.gif);
    z: url(b/subimg/subimg.gif)
    }'''
        assert expected == r.cssText
