"""Testcases for cssutils.css.CSSImportRule"""

import xml.dom

import pytest

import cssutils

from . import test_cssrule


class TestCSSNamespaceRule(test_cssrule.TestCSSRule):
    def _setup_rule(self):
        self.r = cssutils.css.CSSNamespaceRule(namespaceURI='x')
        # self.rRO = cssutils.css.CSSNamespaceRule(namespaceURI='x',
        #                                         readonly=True)
        self.r_type = cssutils.css.CSSRule.NAMESPACE_RULE
        self.r_typeString = 'NAMESPACE_RULE'

    def test_init(self):
        "CSSNamespaceRule.__init__()"
        tests = [
            (None, None),
            ('', ''),
            (None, ''),
            ('', None),
            ('', 'no-uri'),
        ]
        for uri, p in tests:
            r = cssutils.css.CSSNamespaceRule(namespaceURI=uri, prefix=p)
            assert r.namespaceURI is None
            assert '' == r.prefix
            assert '' == r.cssText
            assert r.parentStyleSheet is None
            assert r.parentRule is None

        r = cssutils.css.CSSNamespaceRule(namespaceURI='example')
        assert 'example' == r.namespaceURI
        assert '' == r.prefix
        assert '@namespace "example";' == r.cssText
        self.sheet.add(r)
        assert self.sheet == r.parentStyleSheet

        r = cssutils.css.CSSNamespaceRule(namespaceURI='example', prefix='p')
        assert 'example' == r.namespaceURI
        assert 'p' == r.prefix
        assert '@namespace p "example";' == r.cssText

        css = '@namespace p "u";'
        r = cssutils.css.CSSNamespaceRule(cssText=css)
        assert r.cssText == css

        # only possible to set @... similar name
        with pytest.raises(xml.dom.InvalidModificationErr):
            self.r._setAtkeyword('x')

    def test_cssText(self):
        "CSSNamespaceRule.cssText"
        # cssText may only be set initalially
        r = cssutils.css.CSSNamespaceRule()
        css = '@namespace p "u";'
        r.cssText = css
        assert r.cssText == css
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            r._setCssText('@namespace p "OTHER";')

        tests = {
            '@namespace "";': None,
            '@namespace "u";': None,
            '@namespace empty "";': None,
            '@namespace p "p";': None,
            "@namespace p 'u';": '@namespace p "u";',
            '@\\namespace p "u";': '@namespace p "u";',
            '@NAMESPACE p "u";': '@namespace p "u";',
            '@namespace  p  "u"  ;': '@namespace p "u";',
            '@namespace p"u";': '@namespace p "u";',
            '@namespace p "u";': '@namespace p "u";',
            '@namespace/*1*/"u"/*2*/;': '@namespace /*1*/ "u" /*2*/;',
            '@namespace/*1*/p/*2*/"u"/*3*/;': '@namespace /*1*/ p /*2*/ "u" /*3*/;',
            '@namespace p url(u);': '@namespace p "u";',
            '@namespace p url(\'u\');': '@namespace p "u";',
            '@namespace p url("u");': '@namespace p "u";',
            '@namespace p url( "u" );': '@namespace p "u";',
            # comments
            '@namespace/*1*//*2*/p/*3*//*4*/url(u)/*5*//*6*/;': '@namespace /*1*/ /*2*/ p /*3*/ /*4*/ "u" /*5*/ /*6*/;',
            '@namespace/*1*//*2*/p/*3*//*4*/"u"/*5*//*6*/;': '@namespace /*1*/ /*2*/ p /*3*/ /*4*/ "u" /*5*/ /*6*/;',
            '@namespace/*1*//*2*/p/*3*//*4*/url("u")/*5*//*6*/;': '@namespace /*1*/ /*2*/ p /*3*/ /*4*/ "u" /*5*/ /*6*/;',
            '@namespace/*1*//*2*/url(u)/*5*//*6*/;': '@namespace /*1*/ /*2*/ "u" /*5*/ /*6*/;',
            # WS
            '@namespace\n\r\t\f p\n\r\t\f url(\n\r\t\f u\n\r\t\f )\n\r\t\f ;': '@namespace p "u";',
            '@namespace\n\r\t\f p\n\r\t\f url(\n\r\t\f "u"\n\r\t\f )\n\r\t\f ;': '@namespace p "u";',
            '@namespace\n\r\t\f p\n\r\t\f "str"\n\r\t\f ;': '@namespace p "str";',
            '@namespace\n\r\t\f "str"\n\r\t\f ;': '@namespace "str";',
        }
        self.do_equal_p(tests)
        # self.do_equal_r(tests) # cannot use here as always new r is needed
        for test, expected in list(tests.items()):
            r = cssutils.css.CSSNamespaceRule(cssText=test)
            if expected is None:
                expected = test
            assert expected == r.cssText

        tests = {
            '@namespace;': xml.dom.SyntaxErr,  # nothing
            '@namespace p;': xml.dom.SyntaxErr,  # no namespaceURI
            '@namespace "u" p;': xml.dom.SyntaxErr,  # order
            '@namespace "u";EXTRA': xml.dom.SyntaxErr,
            '@namespace p "u";EXTRA': xml.dom.SyntaxErr,
        }
        self.do_raise_p(tests)  # parse
        tests.update({
            '@namespace p url(x)': xml.dom.SyntaxErr,  # missing ;
            '@namespace p "u"': xml.dom.SyntaxErr,  # missing ;
            # trailing
            '@namespace "u"; ': xml.dom.SyntaxErr,
            '@namespace "u";/**/': xml.dom.SyntaxErr,
            '@namespace p "u"; ': xml.dom.SyntaxErr,
            '@namespace p "u";/**/': xml.dom.SyntaxErr,
        })

        def _do(test):
            cssutils.css.CSSNamespaceRule(cssText=test)

        for test, expected in list(tests.items()):
            with pytest.raises(expected):
                _do(test)

    def test_namespaceURI(self):
        "CSSNamespaceRule.namespaceURI"
        # set only initially
        r = cssutils.css.CSSNamespaceRule(namespaceURI='x')
        assert 'x' == r.namespaceURI
        assert '@namespace "x";' == r.cssText

        r = cssutils.css.CSSNamespaceRule(namespaceURI='"')
        assert '@namespace "\\"";' == r.cssText

        with pytest.raises(xml.dom.NoModificationAllowedErr):
            r._setNamespaceURI('x')

        with pytest.raises(xml.dom.NoModificationAllowedErr):
            r._setCssText('@namespace "u";')

        r._replaceNamespaceURI('http://example.com/new')
        assert 'http://example.com/new' == r.namespaceURI

    def test_prefix(self):
        "CSSNamespaceRule.prefix"
        r = cssutils.css.CSSNamespaceRule(namespaceURI='u')
        r.prefix = 'p'
        assert 'p' == r.prefix
        assert '@namespace p "u";' == r.cssText

        r = cssutils.css.CSSNamespaceRule(cssText='@namespace x "u";')
        r.prefix = 'p'
        assert 'p' == r.prefix
        assert '@namespace p "u";' == r.cssText

        valid = (None, '')
        for prefix in valid:
            r.prefix = prefix
            assert r.prefix == ''
            assert '@namespace "u";' == r.cssText

        valid = ('a', '_x', 'a1', 'a-1')
        for prefix in valid:
            r.prefix = prefix
            assert r.prefix == prefix
            assert '@namespace %s "u";' % prefix == r.cssText

        invalid = ('1', ' x', ' ', ',')
        for prefix in invalid:
            with pytest.raises(xml.dom.SyntaxErr):
                r._setPrefix(prefix)

    def test_InvalidModificationErr(self):
        "CSSNamespaceRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr('@namespace')

    def test_incomplete(self):
        "CSSNamespaceRule (incomplete)"
        tests = {
            '@namespace "uri': '@namespace "uri";',
            "@namespace url(x": '@namespace "x";',
            "@namespace url('x": '@namespace "x";',
            '@namespace url("x;': '@namespace "x;";',
            '@namespace url( "x;': '@namespace "x;";',
            '@namespace url("x ': '@namespace "x ";',
            '@namespace url(x ': '@namespace "x";',
        }
        self.do_equal_p(tests)  # parse
        tests = {
            '@namespace "uri': xml.dom.SyntaxErr,
            "@namespace url(x": xml.dom.SyntaxErr,
            "@namespace url('x": xml.dom.SyntaxErr,
            '@namespace url("x;': xml.dom.SyntaxErr,
            '@namespace url( "x;': xml.dom.SyntaxErr,
            '@namespace url("x ': xml.dom.SyntaxErr,
            '@namespace url(x ': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests)  # set cssText

    def test_reprANDstr(self):
        "CSSNamespaceRule.__repr__(), .__str__()"
        namespaceURI = 'http://example.com'
        prefix = 'prefix'

        s = cssutils.css.CSSNamespaceRule(namespaceURI=namespaceURI, prefix=prefix)

        assert namespaceURI in str(s)
        assert prefix in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert namespaceURI == s2.namespaceURI
        assert prefix == s2.prefix
