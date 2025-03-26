"""Test cases for cssutils.css.CSSStyleRule"""

import xml.dom

import pytest

import cssutils

from . import test_cssrule


class TestCSSStyleRule(test_cssrule.TestCSSRule):
    def _setup_rule(self):
        self.r = cssutils.css.CSSStyleRule()
        self.rRO = cssutils.css.CSSStyleRule(readonly=True)
        self.r_type = cssutils.css.CSSStyleRule.STYLE_RULE
        self.r_typeString = 'STYLE_RULE'

    def test_init(self):
        "CSSStyleRule.type and init"
        super().test_init()
        assert '' == self.r.cssText
        assert isinstance(self.r.selectorList, cssutils.css.selectorlist.SelectorList)
        assert '' == self.r.selectorText
        assert isinstance(self.r.style, cssutils.css.CSSStyleDeclaration)
        assert self.r == self.r.style.parentRule

    def test_refs(self):
        "CSSStyleRule references"
        s = cssutils.css.CSSStyleRule()
        sel, style = s.selectorList, s.style

        assert s == sel.parentRule
        assert s == style.parentRule

        s.cssText = 'a { x:1 }'
        assert sel != s.selectorList
        assert 'a' == s.selectorList.selectorText
        assert style != s.style
        assert '1' == s.style.getPropertyValue('x')

        sel, style = s.selectorList, s.style

        invalids = (
            '$b { x:2 }',  # invalid selector
            'c { $x3 }',  # invalid style
            '/b { 2 }',  # both invalid
        )
        for invalid in invalids:
            try:
                s.cssText = invalid
            except xml.dom.DOMException:
                pass
            assert sel == s.selectorList
            assert 'a' == s.selectorList.selectorText
            assert style == s.style
            assert '1' == s.style.getPropertyValue('x')

        # CHANGING
        s = cssutils.parseString('a {s1: 1}')
        r = s.cssRules[0]
        sel1 = r.selectorList
        st1 = r.style

        # selectorList
        r.selectorText = 'b'
        assert sel1 != r.selectorList
        assert 'b' == r.selectorList.selectorText
        assert 'b' == r.selectorText
        sel1b = r.selectorList

        sel1b.selectorText = 'c'
        assert sel1b == r.selectorList
        assert 'c' == r.selectorList.selectorText
        assert 'c' == r.selectorText

        sel2 = cssutils.css.SelectorList('sel2')
        s.selectorList = sel2
        assert sel2 == s.selectorList
        assert 'sel2' == s.selectorList.selectorText

        sel2.selectorText = 'sel2b'
        assert 'sel2b' == sel2.selectorText
        assert 'sel2b' == s.selectorList.selectorText

        s.selectorList.selectorText = 'sel2c'
        assert 'sel2c' == sel2.selectorText
        assert 'sel2c' == s.selectorList.selectorText

        # style
        r.style = 's1: 2'
        assert st1 != r.style
        assert 's1: 2' == r.style.cssText

        st2 = cssutils.parseStyle('s2: 1')
        r.style = st2
        assert st2 == r.style
        assert 's2: 1' == r.style.cssText

        # cssText
        sl, st = r.selectorList, r.style
        # fails
        try:
            r.cssText = '$ {content: "new"}'
        except xml.dom.SyntaxErr:
            pass
        assert sl == r.selectorList
        assert st == r.style

        r.cssText = 'a {content: "new"}'
        assert sl != r.selectorList
        assert st != r.style

    def test_cssText(self):
        "CSSStyleRule.cssText"
        tests = {
            '* {}': '',
            'a {}': '',
        }
        self.do_equal_p(tests)  # parse
        # self.do_equal_r(tests) # set cssText # TODO: WHY?

        cssutils.ser.prefs.keepEmptyRules = True
        tests = {
            # u'''a{;display:block;float:left}''': 'a {\n    display:block;\n    float:left\n    }', # issue 28
            '''a\n{color: #000}''': 'a {\n    color: #000\n    }',  # issue 4
            '''a\n{color: #000000}''': 'a {\n    color: #000\n    }',  # issue 4
            '''a\n{color: #abc}''': 'a {\n    color: #abc\n    }',  # issue 4
            '''a\n{color: #abcdef}''': 'a {\n    color: #abcdef\n    }',  # issue 4
            '''a\n{color: #00a}''': 'a {\n    color: #00a\n    }',  # issue 4
            '''a\n{color: #1a1a1a}''': 'a {\n    color: #1a1a1a\n    }',  # issue 4
            '''#id\n{ color: red }''': '#id {\n    color: red\n    }',  # issue 3
            '''* {}''': None,
            'a {}': None,
            'b { a: 1; }': 'b {\n    a: 1\n    }',
            # mix of comments and properties
            'c1 {/*1*/a:1;}': 'c1 {\n    /*1*/\n    a: 1\n    }',
            'c2 {a:1;/*2*/}': 'c2 {\n    a: 1;\n    /*2*/\n    }',
            'd1 {/*0*/}': 'd1 {\n    /*0*/\n    }',
            'd2 {/*0*//*1*/}': 'd2 {\n    /*0*/\n    /*1*/\n    }',
            # comments
            # TODO: spaces?
            '''a/*1*//*2*/,/*3*//*4*/b/*5*//*6*/{color: #000}''': 'a/*1*//*2*/, /*3*//*4*/b/*5*//*6*/ {\n    color: #000\n    }',
            '''a,b{color: #000}''': 'a, b {\n    color: #000\n    }',  # issue 4
            '''a\n\r\t\f ,\n\r\t\f b\n\r\t\f {color: #000}''': 'a, b {\n    color: #000\n    }',  # issue 4
        }
        self.do_equal_p(tests)  # parse
        self.do_equal_r(tests)  # set cssText

        tests = {
            '''a;''': xml.dom.SyntaxErr,
            '''a {{}''': xml.dom.SyntaxErr,
            '''a }''': xml.dom.SyntaxErr,
        }
        self.do_raise_p(tests)  # parse
        tests.update({
            '''/*x*/''': xml.dom.SyntaxErr,
            '''a {''': xml.dom.SyntaxErr,
            # trailing
            '''a {}x''': xml.dom.SyntaxErr,
            '''a {/**/''': xml.dom.SyntaxErr,
            '''a {} ''': xml.dom.SyntaxErr,
        })
        self.do_raise_r(tests)  # set cssText

    def test_selectorList(self):
        "CSSStyleRule.selectorList"
        r = cssutils.css.CSSStyleRule()

        r.selectorList.appendSelector('a')
        assert 1 == r.selectorList.length
        assert 'a' == r.selectorText

        r.selectorList.appendSelector(' b  ')
        # only simple selector!
        with pytest.raises(xml.dom.InvalidModificationErr):
            r.selectorList.appendSelector('  h1, x ')

        assert 2 == r.selectorList.length
        assert 'a, b' == r.selectorText

    def test_selectorText(self):
        "CSSStyleRule.selectorText"
        r = cssutils.css.CSSStyleRule()

        r.selectorText = 'a'
        assert 1 == r.selectorList.length
        assert 'a' == r.selectorText

        r.selectorText = ' b, h1  '
        assert 2 == r.selectorList.length
        assert 'b, h1' == r.selectorText

    def test_style(self):
        "CSSStyleRule.style"
        d = cssutils.css.CSSStyleDeclaration()
        self.r.style = d
        assert d.cssText == self.r.style.cssText

        # check if parentRule of d is set
        assert self.r == d.parentRule

    def test_incomplete(self):
        "CSSStyleRule (incomplete)"
        cssutils.ser.prefs.keepEmptyRules = True
        tests = {
            'a {': 'a {}',  # no }
            'a { font-family: "arial sans': 'a {\n    font-family: "arial sans"\n    }',  # no "}
            'a { font-family: "arial sans";': 'a {\n    font-family: "arial sans"\n    }',  # no }
            '''p {
                color: green;
                font-family: 'Courier New Times
                color: red;
                color: green;
                }''': '''p {\n    color: green;\n    color: green\n    }''',
            # no ;
            '''p {
                color: green;
                font-family: 'Courier New Times'
                color: red;
                color: green;
                ''': '''p {\n    color: green;\n    color: green\n    }''',
        }
        self.do_equal_p(tests, raising=False)  # parse

    # TODO:   def test_InvalidModificationErr(self):
    #        "CSSStyleRule.cssText InvalidModificationErr"
    #        self._test_InvalidModificationErr(u'@a a {}')

    def test_reprANDstr(self):
        "CSSStyleRule.__repr__(), .__str__()"
        sel = 'a > b + c'

        s = cssutils.css.CSSStyleRule(selectorText=sel)

        assert sel in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert sel == s2.selectorText

    def test_valid(self):
        "CSSStyleRule.valid"
        rule = cssutils.css.CSSStyleRule(selectorText='*', style='color: red')
        assert rule.valid
        rule.style = 'color: foobar'
        assert not rule.valid
        rule.style = 'foobar: red'
        assert not rule.valid
