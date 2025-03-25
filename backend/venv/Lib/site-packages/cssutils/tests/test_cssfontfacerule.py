"""Testcases for cssutils.css.CSSFontFaceRule"""

# flake8: noqa

import xml.dom
from . import test_cssrule
import cssutils
import pytest


class TestCSSFontFaceRule(test_cssrule.TestCSSRule):
    def _setup_rule(self):
        self.r = cssutils.css.CSSFontFaceRule()
        self.rRO = cssutils.css.CSSFontFaceRule(readonly=True)
        self.r_type = cssutils.css.CSSFontFaceRule.FONT_FACE_RULE  #
        self.r_typeString = 'FONT_FACE_RULE'

    def test_init(self):
        "CSSFontFaceRule.__init__()"
        super().test_init()

        r = cssutils.css.CSSFontFaceRule()
        assert isinstance(r.style, cssutils.css.CSSStyleDeclaration)
        assert r == r.style.parentRule

        # until any properties
        assert '' == r.cssText

        # only possible to set @... similar name
        with pytest.raises(xml.dom.InvalidModificationErr):
            self.r._setAtkeyword('x')

        def checkrefs(ff):
            assert ff == ff.style.parentRule
            for p in ff.style:
                assert ff.style == p.parent

        checkrefs(
            cssutils.css.CSSFontFaceRule(
                style=cssutils.css.CSSStyleDeclaration('font-family: x')
            )
        )

        r = cssutils.css.CSSFontFaceRule()
        r.cssText = '@font-face { font-family: x }'
        checkrefs(r)

        r = cssutils.css.CSSFontFaceRule()
        r.style.setProperty('font-family', 'y')
        checkrefs(r)

        r = cssutils.css.CSSFontFaceRule()
        r.style['font-family'] = 'z'
        checkrefs(r)

        r = cssutils.css.CSSFontFaceRule()
        r.style.fontFamily = 'a'
        checkrefs(r)

    def test_cssText(self):
        "CSSFontFaceRule.cssText"
        tests = {
            '''@font-face {
    font-family: x;
    src: url(../fonts/LateefRegAAT.ttf) format("truetype-aat"), url(../fonts/LateefRegOT.ttf) format("opentype");
    font-style: italic;
    font-weight: 500;
    font-stretch: condensed;
    unicode-range: u+1-ff, u+111
    }''': None,
            '@font-face{font-family: x;}': '@font-face {\n    font-family: x\n    }',
            '@font-face  {  font-family: x;  }': '@font-face {\n    font-family: x\n    }',
            '@f\\ont\\-face{font-family : x;}': '@font-face {\n    font-family: x\n    }',
            # comments
            '@font-face/*1*//*2*/{font-family: x;}': '@font-face /*1*/ /*2*/ {\n    font-family: x\n    }',
            # WS
            '@font-face\n\t\f {\n\t\f font-family:x;\n\t\f }': '@font-face {\n    font-family: x\n    }',
        }
        self.do_equal_r(tests)
        self.do_equal_p(tests)

        tests = {
            '@font-face;': xml.dom.SyntaxErr,
            '@font-face }': xml.dom.SyntaxErr,
        }
        self.do_raise_p(tests)  # parse
        tests.update({
            '@font-face {': xml.dom.SyntaxErr,  # no }
            # trailing
            '@font-face {}1': xml.dom.SyntaxErr,
            '@font-face {}/**/': xml.dom.SyntaxErr,
            '@font-face {} ': xml.dom.SyntaxErr,
        })
        self.do_raise_r(tests)  # set cssText

    def test_style(self):
        "CSSFontFaceRule.style (and references)"
        r = cssutils.css.CSSFontFaceRule()
        s1 = r.style
        assert r == s1.parentRule
        assert '' == s1.cssText

        # set rule.cssText
        r.cssText = '@font-face { font-family: x1 }'
        assert r.style != s1
        assert r == r.style.parentRule
        assert r.cssText == '@font-face {\n    font-family: x1\n    }'
        assert r.style.cssText == 'font-family: x1'
        assert s1.cssText == ''
        s2 = r.style

        # set invalid rule.cssText
        try:
            r.cssText = '@font-face { $ }'
        except xml.dom.SyntaxErr as e:
            pass
        assert r.style == s2
        assert r == s2.parentRule
        assert r.cssText == '@font-face {\n    font-family: x1\n    }'
        assert s2.cssText == 'font-family: x1'
        assert r.style.cssText == 'font-family: x1'

        # set rule.style.cssText
        r.style.cssText = 'font-family: x2'
        assert r.style == s2
        assert r == s2.parentRule
        assert r.cssText == '@font-face {\n    font-family: x2\n    }'
        assert s2.cssText == 'font-family: x2'
        assert r.style.cssText == 'font-family: x2'

        # set new style object s2
        sn = cssutils.css.CSSStyleDeclaration('font-family: y1')
        r.style = sn
        assert r.style == sn
        assert r == sn.parentRule
        assert r.cssText == '@font-face {\n    font-family: y1\n    }'
        assert sn.cssText == 'font-family: y1'
        assert r.style.cssText == 'font-family: y1'
        assert s2.cssText == 'font-family: x2'  # old

        # set s2.cssText
        sn.cssText = 'font-family: y2'
        assert r.style == sn
        assert r.cssText == '@font-face {\n    font-family: y2\n    }'
        assert r.style.cssText == 'font-family: y2'
        assert s2.cssText == 'font-family: x2'  # old

        # set invalid s2.cssText
        try:
            sn.cssText = '$'
        except xml.dom.SyntaxErr as e:
            pass
        assert r.style == sn
        assert r.style.cssText == 'font-family: y2'
        assert r.cssText == '@font-face {\n    font-family: y2\n    }'

        # set r.style with text
        r.style = 'font-family: z'
        assert r.style != sn
        assert r.cssText == '@font-face {\n    font-family: z\n    }'
        assert r.style.cssText == 'font-family: z'
        assert sn.cssText == 'font-family: y2'

    def test_properties(self):
        "CSSFontFaceRule.style properties"
        r = cssutils.css.CSSFontFaceRule()
        r.style.cssText = '''
        src: url(x)
        '''
        exp = '''@font-face {
    src: url(x)
    }'''
        assert exp == r.cssText

        tests = {
            'font-family': [  # ('serif', True),
                #                            ('x', True),
                #                            ('"x"', True),
                ('x, y', False),
                ('"x", y', False),
                ('x, "y"', False),
                #                            ('"x", "y"', False)
            ]
        }
        for n, t in list(tests.items()):
            for v, valid in t:
                r = cssutils.css.CSSFontFaceRule()
                r.style[n] = v
                assert r.style.getProperty(n).parent == r.style
                assert r.style.getProperty(n).valid == valid

    def test_incomplete(self):
        "CSSFontFaceRule (incomplete)"
        tests = {
            '@font-face{': '',  # no } and no content
            '@font-face { ': '',  # no } and no content
            '@font-face { font-family: x': '@font-face {\n    font-family: x\n    }',  # no }
        }
        self.do_equal_p(tests)  # parse

    def test_InvalidModificationErr(self):
        "CSSFontFaceRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr('@font-face')
        tests = {
            '@font-fac {}': xml.dom.InvalidModificationErr,
        }
        self.do_raise_r(tests)

    def test_valid(self):
        "CSSFontFaceRule.valid"
        r = cssutils.css.CSSFontFaceRule()
        assert False == r.valid
        N = 'font-family: x; src: local(x);'
        tests = {
            True: (
                N,
                N + 'font-style: italic; font-weight: bold',
            ),
            False: (
                '',
                'font-family: x, y; src: local(x);',
                N + 'font-style: inherit',
                N + 'invalid: 1',
            ),
        }
        for valid, testlist in list(tests.items()):
            for test in testlist:
                r.style.cssText = test
                assert valid == r.valid

    def test_reprANDstr(self):
        "CSSFontFaceRule.__repr__(), .__str__()"
        style = 'src: url(x)'
        s = cssutils.css.CSSFontFaceRule(style=style)

        assert style in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert style == s2.style.cssText
