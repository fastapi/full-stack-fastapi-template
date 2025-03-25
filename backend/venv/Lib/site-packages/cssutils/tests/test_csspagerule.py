"""Testcases for cssutils.css.CSSPageRule"""

import xml.dom

import pytest

import cssutils

from . import test_cssrule


class TestCSSPageRule(test_cssrule.TestCSSRule):
    def _setup_rule(self):
        self.r = cssutils.css.CSSPageRule()
        self.rRO = cssutils.css.CSSPageRule(readonly=True)
        self.r_type = cssutils.css.CSSPageRule.PAGE_RULE  #
        self.r_typeString = 'PAGE_RULE'

    def test_init(self):
        "CSSPageRule.__init__()"
        super().test_init()

        r = cssutils.css.CSSPageRule()
        assert '' == r.selectorText
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
            cssutils.css.CSSPageRule(
                style=cssutils.css.CSSStyleDeclaration('font-family: x')
            )
        )

        r = cssutils.css.CSSPageRule()
        r.cssText = '@page { font-family: x }'
        checkrefs(r)

        r = cssutils.css.CSSPageRule()
        r.style.setProperty('font-family', 'y')
        checkrefs(r)

        r = cssutils.css.CSSPageRule()
        r.style['font-family'] = 'z'
        checkrefs(r)

        r = cssutils.css.CSSPageRule()
        r.style.fontFamily = 'a'
        checkrefs(r)

    def test_InvalidModificationErr(self):
        "CSSPageRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr('@page')
        tests = {
            '@pag {}': xml.dom.InvalidModificationErr,
        }
        self.do_raise_r(tests)

    def test_incomplete(self):
        "CSSPageRule (incomplete)"
        tests = {
            '@page :left { ': '',  # no } and no content
            '@page :left { color: red': '@page :left {\n    color: red\n    }',  # no }
        }
        self.do_equal_p(tests)  # parse

    def test_cssText(self):
        "CSSPageRule.cssText"
        EXP = '@page %s {\n    margin: 0\n    }'
        tests = {
            '@page {}': '',
            '@page:left{}': '',
            '@page :right {}': '',
            '@page {margin:0;}': '@page {\n    margin: 0\n    }',
            '@page name { margin: 0 }': EXP % 'name',
            '@page name:left { margin: 0 }': EXP % 'name:left',
            '@page name:right { margin: 0 }': EXP % 'name:right',
            '@page name:first { margin: 0 }': EXP % 'name:first',
            '@page :left { margin: 0 }': EXP % ':left',
            '@page:left { margin: 0 }': EXP % ':left',
            '@page :right { margin: 0 }': EXP % ':right',
            '@page :first { margin: 0 }': EXP % ':first',
            '@page :UNKNOWNIDENT { margin: 0 }': EXP % ':UNKNOWNIDENT',
            '@PAGE:left{margin:0;}': '@page :left {\n    margin: 0\n    }',
            '@\\page:left{margin:0;}': '@page :left {\n    margin: 0\n    }',
            # comments
            '@page/*1*//*2*/:left/*3*//*4*/{margin:0;}': '@page /*1*/ /*2*/ :left /*3*/ /*4*/ {\n    margin: 0\n    }',
            # WS
            '@page:left{margin:0;}': '@page :left {\n    margin: 0\n    }',
            '@page\n\r\f\t :left\n\r\f\t {margin:0;}': '@page :left {\n    margin: 0\n    }',
            # MarginRule
            '@page {    @top-right {        content: "2"        }    }': '@page {\n    @top-right {\n        content: "2"\n        }\n    }',
            '@page {padding: 1cm; margin: 1cm; @top-left {content: "1"}@top-right {content: "2";left: 1}}': '@page {\n    padding: 1cm;\n    margin: 1cm;\n    @top-left {\n        content: "1"\n        }\n    @top-right {\n        content: "2";\n        left: 1\n        }\n    }',
            '@page {@top-right { content: "1a"; content: "1b"; x: 1 }@top-right { content: "2"; y: 2 }}': '''@page {\n    @top-right {
        content: "1a";
        content: "1b";
        x: 1;
        content: "2";
        y: 2
        }\n    }''',
        }
        self.do_equal_r(tests)
        self.do_equal_p(tests)

        tests = {
            # auto is not allowed
            '@page AUto {}': xml.dom.SyntaxErr,
            '@page AUto:left {}': xml.dom.SyntaxErr,
            '@page : {}': xml.dom.SyntaxErr,
            '@page :/*1*/left {}': xml.dom.SyntaxErr,
            '@page : left {}': xml.dom.SyntaxErr,
            '@page :left :right {}': xml.dom.SyntaxErr,
            '@page :left a {}': xml.dom.SyntaxErr,
            # no S between IDENT and PSEUDO
            '@page a :left  {}': xml.dom.SyntaxErr,
            '@page :left;': xml.dom.SyntaxErr,
            '@page :left }': xml.dom.SyntaxErr,
        }
        self.do_raise_p(tests)  # parse
        tests.update({
            # false selector
            '@page :right :left {}': xml.dom.SyntaxErr,  # no }
            '@page :right X {}': xml.dom.SyntaxErr,  # no }
            '@page X Y {}': xml.dom.SyntaxErr,  # no }
            '@page :left {': xml.dom.SyntaxErr,  # no }
            # trailing
            '@page :left {}1': xml.dom.SyntaxErr,  # no }
            '@page :left {}/**/': xml.dom.SyntaxErr,  # no }
            '@page :left {} ': xml.dom.SyntaxErr,  # no }
        })
        self.do_raise_r(tests)  # set cssText

    def test_cssText2(self):
        "CSSPageRule.cssText 2"
        r = cssutils.css.CSSPageRule()
        s = 'a:left'
        r.selectorText = s
        assert r.selectorText == s

        st = 'size: a4'
        r.style = st
        assert r.style.cssText == st

        # invalid selector
        with pytest.raises(xml.dom.SyntaxErr):
            r._setStyle('$')
        assert r.selectorText == s
        assert r.style.cssText == st

        with pytest.raises(xml.dom.SyntaxErr):
            r._setCssText('@page $ { color: red }')
        assert r.selectorText == s
        assert r.style.cssText == st

        # invalid style
        with pytest.raises(xml.dom.SyntaxErr):
            r._setSelectorText('$')
        assert r.selectorText == s
        assert r.style.cssText == st

        with pytest.raises(xml.dom.SyntaxErr):
            r._setCssText('@page b:right { x }')
        assert r.selectorText == s
        assert r.style.cssText == st

    def test_selectorText(self):
        "CSSPageRule.selectorText"
        r = cssutils.css.CSSPageRule()
        r.selectorText = 'a:left'
        assert r.selectorText == 'a:left'

        tests = {
            '': '',
            'name': None,
            ':right': None,
            ':first': None,
            ':UNKNOWNIDENT': None,
            'name:left': None,
            ' :left': ':left',
            ':left': ':left',
            '/*1*/:left/*a*/': '/*1*/ :left /*a*/',
            '/*1*/ :left /*a*/ /*b*/': None,
            ':left/*a*/': ':left /*a*/',
            '/*1*/:left': '/*1*/ :left',
        }
        self.do_equal_r(tests, att='selectorText')

        tests = {
            ':': xml.dom.SyntaxErr,
            ':/*1*/left': xml.dom.SyntaxErr,
            ': left': xml.dom.SyntaxErr,
            ':left :right': xml.dom.SyntaxErr,
            ':left a': xml.dom.SyntaxErr,
            'name :left': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests, att='_setSelectorText')

    def test_specificity(self):
        "CSSPageRule.specificity"
        r = cssutils.css.CSSPageRule()
        tests = {
            '': (0, 0, 0),
            'name': (1, 0, 0),
            ':first': (0, 1, 0),
            ':left': (0, 0, 1),
            ':right': (0, 0, 1),
            ':UNKNOWNIDENT': (0, 0, 1),
            'name:first': (1, 1, 0),
            'name:left': (1, 0, 1),
            'name:right': (1, 0, 1),
            'name:X': (1, 0, 1),
        }
        for sel, exp in list(tests.items()):
            r.selectorText = sel
            assert r.specificity == exp

            r = cssutils.css.CSSPageRule()
            r.cssText = '@page %s {}' % sel
            assert r.specificity == exp

    def test_cssRules(self):
        "CSSPageRule.cssRules"
        s = cssutils.parseString('@page {}')
        p = s.cssRules[0]

        assert len(p.cssRules) == 0

        # add and insert
        m1 = cssutils.css.MarginRule('@top-left', 'color: red')
        i = p.add(m1)
        assert i == 0
        assert len(p.cssRules) == 1

        m3 = cssutils.css.MarginRule()
        m3.cssText = '@top-right { color: blue }'
        i = p.insertRule(m3)
        assert i == 1
        assert len(p.cssRules) == 2

        m2 = cssutils.css.MarginRule()
        m2.margin = '@top-center'
        m2.style = 'color: green'
        i = p.insertRule(m2, 1)
        assert i == 1
        assert len(p.cssRules) == 3

        assert (
            p.cssText
            == '''@page {
    @top-left {
        color: red
        }
    @top-center {
        color: green
        }
    @top-right {
        color: blue
        }
    }'''
        )

        # keys and dict index
        assert '@top-left' in p
        assert '@bottom-left' not in p

        assert list(p.keys()) == ['@top-left', '@top-center', '@top-right']

        assert p['@bottom-left'] is None
        assert p['@top-left'].cssText == 'color: red'
        p['@top-left'] = 'color: #f00'
        assert p['@top-left'].cssText == 'color: #f00'

        # delete
        p.deleteRule(m2)
        assert len(p.cssRules) == 2
        assert (
            p.cssText
            == '''@page {
    @top-left {
        color: #f00
        }
    @top-right {
        color: blue
        }
    }'''
        )

        p.deleteRule(0)
        assert len(p.cssRules) == 1
        assert m3 == p.cssRules[0]
        assert (
            p.cssText
            == '''@page {
    @top-right {
        color: blue
        }
    }'''
        )

        del p['@top-right']
        assert len(p.cssRules) == 0

    def test_style(self):
        "CSSPageRule.style (and references)"
        r = cssutils.css.CSSPageRule()
        s1 = r.style
        assert r == s1.parentRule
        assert '' == s1.cssText

        # set rule.cssText
        r.cssText = '@page { font-family: x1 }'
        assert r.style != s1
        assert r == r.style.parentRule
        assert r.cssText == '@page {\n    font-family: x1\n    }'
        assert r.style.cssText == 'font-family: x1'
        assert s1.cssText == ''
        s2 = r.style

        # set invalid rule.cssText
        try:
            r.cssText = '@page { $ }'
        except xml.dom.SyntaxErr:
            pass
        assert r.style == s2
        assert r == r.style.parentRule
        assert r.cssText == '@page {\n    font-family: x1\n    }'
        assert r.style.cssText == 'font-family: x1'
        assert s2.cssText == 'font-family: x1'
        s3 = r.style

        # set rule.style.cssText
        r.style.cssText = 'font-family: x2'
        assert r.style == s3
        assert r == r.style.parentRule
        assert r.cssText == '@page {\n    font-family: x2\n    }'
        assert r.style.cssText == 'font-family: x2'

        # set new style object s2
        s2 = cssutils.css.CSSStyleDeclaration('font-family: y1')
        r.style = s2
        assert r.style == s2
        assert r == s2.parentRule
        assert r.cssText == '@page {\n    font-family: y1\n    }'
        assert s2.cssText == 'font-family: y1'
        assert r.style.cssText == 'font-family: y1'
        assert s3.cssText == 'font-family: x2'  # old

        # set s2.cssText
        s2.cssText = 'font-family: y2'
        assert r.style == s2
        assert r.cssText == '@page {\n    font-family: y2\n    }'
        assert r.style.cssText == 'font-family: y2'
        assert s3.cssText == 'font-family: x2'  # old
        # set invalid s2.cssText
        try:
            s2.cssText = '$'
        except xml.dom.SyntaxErr:
            pass
        assert r.style == s2
        assert r.cssText == '@page {\n    font-family: y2\n    }'
        assert r.style.cssText == 'font-family: y2'
        assert s3.cssText == 'font-family: x2'  # old

        # set r.style with text
        r.style = 'font-family: z'
        assert r.style != s2
        assert r.cssText == '@page {\n    font-family: z\n    }'
        assert r.style.cssText == 'font-family: z'

    def test_properties(self):
        "CSSPageRule.style properties"
        r = cssutils.css.CSSPageRule()
        r.style.cssText = '''
        margin-top: 0;
        margin-right: 0;
        margin-bottom: 0;
        margin-left: 0;
        margin: 0;

        page-break-before: auto;
        page-break-after: auto;
        page-break-inside: auto;

        orphans: 3;
        widows: 3;
        '''
        exp = '''@page {
    margin-top: 0;
    margin-right: 0;
    margin-bottom: 0;
    margin-left: 0;
    margin: 0;
    page-break-before: auto;
    page-break-after: auto;
    page-break-inside: auto;
    orphans: 3;
    widows: 3
    }'''
        assert exp == r.cssText

    def test_reprANDstr(self):
        "CSSPageRule.__repr__(), .__str__()"
        sel = ':left'

        s = cssutils.css.CSSPageRule(selectorText=sel)

        assert sel in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert sel == s2.selectorText
