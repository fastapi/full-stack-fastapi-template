"""Testcases for cssutils.css.CSSImportRule"""

import re
import xml.dom

import pytest

import cssutils

from . import test_cssrule


class TestCSSImportRule(test_cssrule.TestCSSRule):
    def _setup_rule(self):
        self.r = cssutils.css.CSSImportRule()
        self.rRO = cssutils.css.CSSImportRule(readonly=True)
        self.r_type = cssutils.css.CSSImportRule.IMPORT_RULE
        self.r_typeString = 'IMPORT_RULE'

    def test_init(self):
        "CSSImportRule.__init__()"
        super().test_init()

        # no init param
        assert self.r.href is None
        assert self.r.hreftype is None
        assert not self.r.hrefFound
        assert 'all' == self.r.media.mediaText
        assert isinstance(self.r.media, cssutils.stylesheets.MediaList)
        assert self.r.name is None
        assert isinstance(self.r.styleSheet, cssutils.css.CSSStyleSheet)
        assert 0 == self.r.styleSheet.cssRules.length
        assert '' == self.r.cssText

        # all
        r = cssutils.css.CSSImportRule(href='href', mediaText='tv', name='name')
        assert '@import url(href) tv "name";' == r.cssText
        assert "href" == r.href
        assert r.hreftype is None
        assert 'tv' == r.media.mediaText
        assert isinstance(r.media, cssutils.stylesheets.MediaList)
        assert 'name' == r.name
        assert r.parentRule is None  # see CSSRule
        assert r.parentStyleSheet is None  # see CSSRule
        assert isinstance(self.r.styleSheet, cssutils.css.CSSStyleSheet)
        assert 0 == self.r.styleSheet.cssRules.length

        # href
        r = cssutils.css.CSSImportRule('x')
        assert '@import url(x);' == r.cssText
        assert 'x' == r.href
        assert r.hreftype is None

        # href + mediaText
        r = cssutils.css.CSSImportRule('x', 'print')
        assert '@import url(x) print;' == r.cssText
        assert 'x' == r.href
        assert 'print' == r.media.mediaText

        # href + name
        r = cssutils.css.CSSImportRule('x', name='n')
        assert '@import url(x) "n";' == r.cssText
        assert 'x' == r.href
        assert 'n' == r.name

        # href + mediaText + name
        r = cssutils.css.CSSImportRule('x', 'print', 'n')
        assert '@import url(x) print "n";' == r.cssText
        assert 'x' == r.href
        assert 'print' == r.media.mediaText
        assert 'n' == r.name

        # media +name only
        self.r = cssutils.css.CSSImportRule(mediaText='print', name="n")
        assert isinstance(self.r.media, cssutils.stylesheets.MediaList)
        assert '' == self.r.cssText
        assert 'print' == self.r.media.mediaText
        assert 'n' == self.r.name

        # only possible to set @... similar name
        with pytest.raises(xml.dom.InvalidModificationErr):
            self.r._setAtkeyword('x')

    def test_cssText(self):
        "CSSImportRule.cssText"
        tests = {
            # href string
            '''@import "str";''': None,
            '''@import"str";''': '''@import "str";''',
            '''@\\import "str";''': '''@import "str";''',
            '''@IMPORT "str";''': '''@import "str";''',
            '''@import 'str';''': '''@import "str";''',
            '''@import 'str' ;''': '''@import "str";''',
            '''@import "str"  ;''': '''@import "str";''',
            r'''@import "\""  ;''': r'''@import "\"";''',
            '''@import '\\'';''': r'''@import "'";''',
            '''@import '"';''': r'''@import "\"";''',
            # href url
            '''@import url(x.css);''': None,
            # nospace
            '''@import url(")");''': '''@import url(")");''',
            '''@import url("\\"");''': '''@import url("\\"");''',
            '''@import url('\\'');''': '''@import url("'");''',
            # href + media
            # all is removed
            '''@import "str" all;''': '''@import "str";''',
            '''@import "str" tv, print;''': None,
            '''@import"str"tv,print;''': '''@import "str" tv, print;''',
            '''@import "str" tv, print, all;''': '''@import "str";''',
            '''@import "str" handheld, all;''': '''@import "str";''',
            '''@import "str" all, handheld;''': '''@import "str";''',
            '''@import "str" not tv;''': None,
            '''@import "str" only tv;''': None,
            '''@import "str" only tv and (color: 2);''': None,
            # href + name
            '''@import "str" "name";''': None,
            '''@import "str" 'name';''': '''@import "str" "name";''',
            '''@import url(x) "name";''': None,
            '''@import "str" "\\"";''': None,
            '''@import "str" '\\'';''': '''@import "str" "'";''',
            # href + media + name
            '''@import"str"tv"name";''': '''@import "str" tv "name";''',
            '''@import\t\r\f\n"str"\t\t\r\f\ntv\t\t\r\f\n"name"\t;''': '''@import "str" tv "name";''',
            # comments
            '''@import /*1*/ "str" /*2*/;''': None,
            '@import/*1*//*2*/"str"/*3*//*4*/all/*5*//*6*/"name"/*7*//*8*/ ;': '@import /*1*/ /*2*/ "str" /*3*/ /*4*/ all /*5*/ /*6*/ "name" /*7*/ /*8*/;',
            '@import/*1*//*2*/url(u)/*3*//*4*/all/*5*//*6*/"name"/*7*//*8*/ ;': '@import /*1*/ /*2*/ url(u) /*3*/ /*4*/ all /*5*/ /*6*/ "name" /*7*/ /*8*/;',
            '@import/*1*//*2*/url("u")/*3*//*4*/all/*5*//*6*/"name"/*7*//*8*/ ;': '@import /*1*/ /*2*/ url(u) /*3*/ /*4*/ all /*5*/ /*6*/ "name" /*7*/ /*8*/;',
            # WS
            '@import\n\t\f "str"\n\t\f tv\n\t\f "name"\n\t\f ;': '@import "str" tv "name";',
            '@import\n\t\f url(\n\t\f u\n\t\f )\n\t\f tv\n\t\f "name"\n\t\f ;': '@import url(u) tv "name";',
            '@import\n\t\f url("u")\n\t\f tv\n\t\f "name"\n\t\f ;': '@import url(u) tv "name";',
            '@import\n\t\f url(\n\t\f "u"\n\t\f )\n\t\f tv\n\t\f "name"\n\t\f ;': '@import url(u) tv "name";',
        }
        self.do_equal_r(tests)  # set cssText
        tests.update({
            '@import "x.css" tv': '@import "x.css" tv;',
            '@import "x.css"': '@import "x.css";',  # no ;
            "@import 'x.css'": '@import "x.css";',  # no ;
            '@import url(x.css)': '@import url(x.css);',  # no ;
            '@import "x;': '@import "x;";',  # no "!
        })
        self.do_equal_p(tests)  # parse

        tests = {
            '''@import;''': xml.dom.SyntaxErr,
            '''@import all;''': xml.dom.SyntaxErr,
            '''@import all"name";''': xml.dom.SyntaxErr,
            '''@import x";''': xml.dom.SyntaxErr,
            '''@import "str" ,all;''': xml.dom.SyntaxErr,
            '''@import "str" all,;''': xml.dom.SyntaxErr,
            '''@import "str" all tv;''': xml.dom.SyntaxErr,
            '''@import "str" "name" all;''': xml.dom.SyntaxErr,
        }
        self.do_raise_p(tests)  # parse
        tests.update({
            '@import "x.css"': xml.dom.SyntaxErr,
            "@import 'x.css'": xml.dom.SyntaxErr,
            '@import url(x.css)': xml.dom.SyntaxErr,
            '@import "x.css" tv': xml.dom.SyntaxErr,
            '@import "x;': xml.dom.SyntaxErr,
            '''@import url("x);''': xml.dom.SyntaxErr,
            # trailing
            '''@import "x";"a"''': xml.dom.SyntaxErr,
            # trailing S or COMMENT
            '''@import "x";/**/''': xml.dom.SyntaxErr,
            '''@import "x"; ''': xml.dom.SyntaxErr,
        })
        self.do_raise_r(tests)  # set cssText

    def test_href(self):
        "CSSImportRule.href"
        # set
        self.r.href = 'x'
        assert 'x' == self.r.href
        assert '@import url(x);' == self.r.cssText

        # http
        self.r.href = 'http://www.example.com/x?css=z&v=1'
        assert 'http://www.example.com/x?css=z&v=1' == self.r.href
        assert '@import url(http://www.example.com/x?css=z&v=1);' == self.r.cssText

        # also if hreftype changed
        self.r.hreftype = 'string'
        assert 'http://www.example.com/x?css=z&v=1' == self.r.href
        assert '@import "http://www.example.com/x?css=z&v=1";' == self.r.cssText

        # string escaping?
        self.r.href = '"'
        assert '@import "\\"";' == self.r.cssText
        self.r.hreftype = 'url'
        assert '@import url("\\"");' == self.r.cssText

        # url escaping?
        self.r.href = ')'
        assert '@import url(")");' == self.r.cssText

        self.r.hreftype = 'NOT VALID'  # using default
        assert '@import url(")");' == self.r.cssText

    def test_hrefFound(self):
        "CSSImportRule.hrefFound"

        def fetcher(url):
            if url == 'http://example.com/yes':
                return None, '/**/'
            else:
                return None, None

        parser = cssutils.CSSParser(fetcher=fetcher)
        sheet = parser.parseString('@import "http://example.com/yes" "name"')

        r = sheet.cssRules[0]
        assert b'/**/' == r.styleSheet.cssText
        assert r.hrefFound
        assert 'name' == r.name

        r.cssText = '@import url(http://example.com/none) "name2";'
        assert b'' == r.styleSheet.cssText
        assert not r.hrefFound
        assert 'name2' == r.name

        sheet.cssText = '@import url(http://example.com/none);'
        assert r != sheet.cssRules[0]

    def test_hreftype(self):
        "CSSImportRule.hreftype"
        self.r = cssutils.css.CSSImportRule()

        self.r.cssText = '@import /*1*/url(org) /*2*/;'
        assert 'uri' == self.r.hreftype
        assert '@import /*1*/ url(org) /*2*/;' == self.r.cssText

        self.r.cssText = '@import /*1*/"org" /*2*/;'
        assert 'string' == self.r.hreftype
        assert '@import /*1*/ "org" /*2*/;' == self.r.cssText

        self.r.href = 'new'
        assert '@import /*1*/ "new" /*2*/;' == self.r.cssText

        self.r.hreftype = 'uri'
        assert '@import /*1*/ url(new) /*2*/;' == self.r.cssText

    def test_media(self):
        "CSSImportRule.media"
        self.r.href = 'x'  # @import url(x)

        # media is readonly
        with pytest.raises(AttributeError):
            self.r.__setattr__('media', None)

        # but not static
        self.r.media.mediaText = 'print'
        assert '@import url(x) print;' == self.r.cssText
        self.r.media.appendMedium('tv')
        assert '@import url(x) print, tv;' == self.r.cssText

        tv_msg = re.escape(
            '''MediaList: Ignoring new medium '''
            '''cssutils.stylesheets.MediaQuery(mediaText='tv') '''
            '''as already specified "all" (set ``mediaText`` instead).'''
        )

        # for generated rule
        r = cssutils.css.CSSImportRule(href='x')
        with pytest.raises(xml.dom.InvalidModificationErr, match=tv_msg):
            r.media.appendMedium('tv')
        assert '@import url(x);' == r.cssText
        with pytest.raises(xml.dom.InvalidModificationErr, match=tv_msg):
            r.media.appendMedium('tv')
        assert '@import url(x);' == r.cssText
        r.media.mediaText = 'tv'
        assert '@import url(x) tv;' == r.cssText
        r.media.appendMedium('print')  # all + tv = all!
        assert '@import url(x) tv, print;' == r.cssText

        # for parsed rule without initial media
        s = cssutils.parseString('@import url(x);')
        r = s.cssRules[0]

        with pytest.raises(xml.dom.InvalidModificationErr, match=tv_msg):
            r.media.appendMedium('tv')
        assert '@import url(x);' == r.cssText
        with pytest.raises(xml.dom.InvalidModificationErr, match=tv_msg):
            r.media.appendMedium('tv')
        assert '@import url(x);' == r.cssText
        r.media.mediaText = 'tv'
        assert '@import url(x) tv;' == r.cssText
        r.media.appendMedium('print')  # all + tv = all!
        assert '@import url(x) tv, print;' == r.cssText

    def test_name(self):
        "CSSImportRule.name"
        r = cssutils.css.CSSImportRule('x', name='a000000')
        assert 'a000000' == r.name
        assert '@import url(x) "a000000";' == r.cssText

        r.name = "n"
        assert 'n' == r.name
        assert '@import url(x) "n";' == r.cssText
        r.name = '"'
        assert '"' == r.name
        assert '@import url(x) "\\"";' == r.cssText

        r.hreftype = 'string'
        assert '@import "x" "\\"";' == r.cssText
        r.name = "123"
        assert '@import "x" "123";' == r.cssText

        r.name = None
        assert r.name is None
        assert '@import "x";' == r.cssText

        r.name = ""
        assert r.name is None
        assert '@import "x";' == r.cssText

        with pytest.raises(xml.dom.SyntaxErr):
            r._setName(0)
        with pytest.raises(xml.dom.SyntaxErr):
            r._setName(123)

    def test_styleSheet(self):
        "CSSImportRule.styleSheet"

        def fetcher(url):
            if url == "/root/level1/anything.css":
                return None, '@import "level2/css.css" "title2";'
            else:
                return None, 'a { color: red }'

        parser = cssutils.CSSParser(fetcher=fetcher)
        sheet = parser.parseString(
            '''@charset "ascii";
                                   @import "level1/anything.css" tv "title";''',
            href='/root/',
        )

        assert sheet.href == '/root/'

        ir = sheet.cssRules[1]
        assert ir.href == 'level1/anything.css'
        assert ir.styleSheet.href == '/root/level1/anything.css'
        # inherits ascii as no self charset is set
        assert ir.styleSheet.encoding == 'ascii'
        assert ir.styleSheet.ownerRule == ir
        assert ir.styleSheet.media.mediaText == 'tv'
        assert ir.styleSheet.parentStyleSheet is None  # sheet
        assert ir.styleSheet.title == 'title'
        assert (
            ir.styleSheet.cssText
            == b'@charset "ascii";\n@import "level2/css.css" "title2";'
        )

        ir2 = ir.styleSheet.cssRules[1]
        assert ir2.href == 'level2/css.css'
        assert ir2.styleSheet.href == '/root/level1/level2/css.css'
        # inherits ascii as no self charset is set
        assert ir2.styleSheet.encoding == 'ascii'
        assert ir2.styleSheet.ownerRule == ir2
        assert ir2.styleSheet.media.mediaText == 'all'
        assert ir2.styleSheet.parentStyleSheet is None  # ir.styleSheet
        assert ir2.styleSheet.title == 'title2'
        assert (
            ir2.styleSheet.cssText == b'@charset "ascii";\na {\n    color: red\n    }'
        )

        sheet = cssutils.parseString('@import "CANNOT-FIND.css";')
        ir = sheet.cssRules[0]
        assert ir.href == "CANNOT-FIND.css"
        assert isinstance(ir.styleSheet, cssutils.css.CSSStyleSheet)

        def fetcher(url):
            if url.endswith('level1.css'):
                return None, b'@charset "ascii"; @import "level2.css";'
            else:
                return None, b'a { color: red }'

        parser = cssutils.CSSParser(fetcher=fetcher)

        sheet = parser.parseString('@charset "iso-8859-1";@import "level1.css";')
        assert sheet.encoding == 'iso-8859-1'

        sheet = sheet.cssRules[1].styleSheet
        assert sheet.encoding == 'ascii'

        sheet = sheet.cssRules[1].styleSheet
        assert sheet.encoding == 'ascii'

    def test_incomplete(self):
        "CSSImportRule (incomplete)"
        tests = {
            '@import "x.css': '@import "x.css";',
            "@import 'x": '@import "x";',
            # TODO:
            "@import url(x": '@import url(x);',
            "@import url('x": '@import url(x);',
            '@import url("x;': '@import url("x;");',
            '@import url( "x;': '@import url("x;");',
            '@import url("x ': '@import url("x ");',
            '@import url(x ': '@import url(x);',
            '''@import "a
                @import "b";
                @import "c";''': '@import "c";',
        }
        self.do_equal_p(tests, raising=False)  # parse

    def test_InvalidModificationErr(self):
        "CSSImportRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr('@import')

    def test_reprANDstr(self):
        "CSSImportRule.__repr__(), .__str__()"
        href = 'x.css'
        mediaText = 'tv, print'
        name = 'name'
        s = cssutils.css.CSSImportRule(href=href, mediaText=mediaText, name=name)

        # str(): mediaText nor name are present here
        assert href in str(s)

        # repr()
        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert href == s2.href
        assert mediaText == s2.media.mediaText
        assert name == s2.name
