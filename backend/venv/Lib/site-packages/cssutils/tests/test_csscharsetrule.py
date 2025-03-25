"""Testcases for cssutils.css.CSSCharsetRule"""

import xml.dom

import pytest

import cssutils.css

from . import test_cssrule


class TestCSSCharsetRule(test_cssrule.TestCSSRule):
    def _setup_rule(self):
        self.r = cssutils.css.CSSCharsetRule()
        self.rRO = cssutils.css.CSSCharsetRule(readonly=True)
        self.r_type = cssutils.css.CSSCharsetRule.CHARSET_RULE
        self.r_typeString = 'CHARSET_RULE'

    def test_init(self):
        "CSSCharsetRule.__init__()"
        super().test_init()
        assert self.r.encoding is None
        assert '' == self.r.cssText

        with pytest.raises(xml.dom.InvalidModificationErr):
            self.r._setCssText('xxx')

    def test_InvalidModificationErr(self):
        "CSSCharsetRule InvalidModificationErr"
        self._test_InvalidModificationErr('@charset')

    def test_init_encoding(self):
        "CSSCharsetRule.__init__(encoding)"
        for enc in (None, 'UTF-8', 'utf-8', 'iso-8859-1', 'ascii'):
            r = cssutils.css.CSSCharsetRule(enc)
            if enc is None:
                assert r.encoding is None
                assert '' == r.cssText
            else:
                assert enc.lower() == r.encoding
                assert '@charset "%s";' % enc.lower() == r.cssText

        for enc in (' ascii ', ' ascii', 'ascii '):
            with pytest.raises(xml.dom.SyntaxErr, match="Syntax Error"):
                cssutils.css.CSSCharsetRule(enc)

        for enc in ('unknown',):
            with pytest.raises(xml.dom.SyntaxErr, match=r"Unknown \(Python\) encoding"):
                cssutils.css.CSSCharsetRule(enc)

    def test_encoding(self):
        "CSSCharsetRule.encoding"
        for enc in ('UTF-8', 'utf-8', 'iso-8859-1', 'ascii'):
            self.r.encoding = enc
            assert enc.lower() == self.r.encoding
            assert '@charset "%s";' % enc.lower() == self.r.cssText

        for enc in (None, ' ascii ', ' ascii', 'ascii '):
            with pytest.raises(xml.dom.SyntaxErr, match="Syntax Error"):
                self.r.encoding = enc

        for enc in ('unknown',):
            with pytest.raises(xml.dom.SyntaxErr, match=r"Unknown \(Python\) encoding"):
                self.r.encoding = enc

    def test_cssText(self):
        """CSSCharsetRule.cssText

        setting cssText is ok to use @CHARSET or other but a file
        using parse MUST use ``@charset "ENCODING";``
        """
        tests = {
            '@charset "utf-8";': None,
            "@charset 'utf-8';": '@charset "utf-8";',
        }
        self.do_equal_r(tests)
        self.do_equal_p(tests)  # also parse

        tests = {
            # token is "@charset " with space!
            '@charset;"': xml.dom.InvalidModificationErr,
            '@CHARSET "UTF-8";': xml.dom.InvalidModificationErr,
            '@charset "";': xml.dom.SyntaxErr,
            '''@charset /*1*/"utf-8"/*2*/;''': xml.dom.SyntaxErr,
            '''@charset /*1*/"utf-8";''': xml.dom.SyntaxErr,
            '''@charset "utf-8"/*2*/;''': xml.dom.SyntaxErr,
            '@charset { utf-8 }': xml.dom.SyntaxErr,
            '@charset "utf-8"': xml.dom.SyntaxErr,
            '@charset a;': xml.dom.SyntaxErr,
            '@charset /**/;': xml.dom.SyntaxErr,
            # trailing content
            '@charset "utf-8";s': xml.dom.SyntaxErr,
            '@charset "utf-8";/**/': xml.dom.SyntaxErr,
            '@charset "utf-8"; ': xml.dom.SyntaxErr,
            # comments do not work in this rule!
            '@charset "utf-8"/*1*//*2*/;': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests)

    def test_repr(self):
        "CSSCharsetRule.__repr__()"
        self.r.encoding = 'utf-8'
        assert 'utf-8' in repr(self.r)

    def test_reprANDstr(self):
        "CSSCharsetRule.__repr__(), .__str__()"
        encoding = 'utf-8'

        s = cssutils.css.CSSCharsetRule(encoding=encoding)

        assert encoding in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert encoding == s2.encoding
