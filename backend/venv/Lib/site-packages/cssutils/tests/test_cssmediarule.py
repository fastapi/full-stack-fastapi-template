"""Testcases for cssutils.css.CSSMediaRule"""

# flake8: noqa

import xml.dom
from . import test_cssrule
import cssutils
import pytest


class TestCSSMediaRule(test_cssrule.TestCSSRule):
    def _setup_rule(self):
        self.r = cssutils.css.CSSMediaRule()
        self.rRO = cssutils.css.CSSMediaRule(readonly=True)
        self.r_type = cssutils.css.CSSMediaRule.MEDIA_RULE
        self.r_typeString = 'MEDIA_RULE'
        # for tests
        self.stylerule = cssutils.css.CSSStyleRule()
        self.stylerule.cssText = 'a {}'

    def test_init(self):
        "CSSMediaRule.__init__()"
        super().test_init()

        r = cssutils.css.CSSMediaRule()
        assert isinstance(r.cssRules, cssutils.css.CSSRuleList)
        assert [] == r.cssRules
        assert '' == r.cssText
        assert isinstance(r.media, cssutils.stylesheets.MediaList)
        assert 'all' == r.media.mediaText
        assert r.name is None

        r = cssutils.css.CSSMediaRule(mediaText='print', name='name')
        assert isinstance(r.cssRules, cssutils.css.CSSRuleList)
        assert [] == r.cssRules
        assert '' == r.cssText
        assert isinstance(r.media, cssutils.stylesheets.MediaList)
        assert 'print' == r.media.mediaText
        assert 'name' == r.name

        # only possible to set @... similar name
        with pytest.raises(xml.dom.InvalidModificationErr):
            self.r._setAtkeyword('x')

    def test_iter(self):
        "CSSMediaRule.__iter__()"
        m = cssutils.css.CSSMediaRule()
        m.cssText = '''@media all { /*1*/a { left: 0} b{ top:0} }'''
        types = [
            cssutils.css.CSSRule.COMMENT,
            cssutils.css.CSSRule.STYLE_RULE,
            cssutils.css.CSSRule.STYLE_RULE,
        ]
        for i, rule in enumerate(m):
            assert rule == m.cssRules[i]
            assert rule.type == types[i]
            assert rule.parentRule == m

    def test_refs(self):
        """CSSStylesheet references"""
        s = cssutils.parseString('@media all {a {color: red}}')
        r = s.cssRules[0]
        rules = r.cssRules
        assert r.cssRules[0].parentStyleSheet == s
        assert rules[0].parentStyleSheet == s

        # set cssText
        r.cssText = '@media all {a {color: blue}}'
        # not anymore: self.assertEqual(rules, r.cssRules)

        # set cssRules
        r.cssRules = cssutils.parseString(
            '''
            /**/
            @x;
            b {}').cssRules'''
        ).cssRules
        # new object
        assert rules != r.cssRules
        for i, sr in enumerate(r.cssRules):
            assert sr.parentStyleSheet == s
            assert sr.parentRule == r

    def test_cssRules(self):
        "CSSMediaRule.cssRules"
        r = cssutils.css.CSSMediaRule()
        assert [] == r.cssRules
        sr = cssutils.css.CSSStyleRule()
        r.cssRules.append(sr)
        assert [sr] == r.cssRules
        ir = cssutils.css.CSSImportRule()
        with pytest.raises(xml.dom.HierarchyRequestErr):
            r.cssRules.append(ir)

        s = cssutils.parseString('@media all { /*1*/a {x:1} }')
        m = s.cssRules[0]
        assert 2 == m.cssRules.length
        del m.cssRules[0]
        assert 1 == m.cssRules.length
        m.cssRules.append('/*2*/')
        assert 2 == m.cssRules.length
        m.cssRules.extend(cssutils.parseString('/*3*/x {y:2}').cssRules)
        assert 4 == m.cssRules.length
        assert (
            '@media all {\n    a {\n        x: 1\n        }\n    /*2*/\n    /*3*/\n    x {\n        y: 2\n        }\n    }'
            == m.cssText
        )

        for rule in m.cssRules:
            assert rule.parentStyleSheet == s
            assert rule.parentRule == m

    def test_cssText(self):
        "CSSMediaRule.cssText"
        style = '''{
    a {
        color: red
        }
    }'''

        mls = {
            ' (min-device-pixel-ratio: 1.3), (min-resolution: 1.3dppx) ': None,
            ' tv ': None,
            ' only tv ': None,
            ' not tv ': None,
            ' only tv and (color) ': None,
            ' only tv and(color)': ' only tv and (color) ',
            ' only tv and (color: red) ': None,
            ' only tv and (color: red) and (width: 100px) ': None,
            ' only tv and (color: red) and (width: 100px), tv ': None,
            ' only tv and (color: red) and (width: 100px), tv and (width: 20px) ': None,
            ' only tv and(color :red)and(  width :100px  )  ,tv and(width: 20px) ': ' only tv and (color: red) and (width: 100px), tv and (width: 20px) ',
            ' (color: red) and (width: 100px), (width: 20px) ': None,
            ' /*1*/ only /*2*/ tv /*3*/ and /*4*/ (/*5*/ width) /*5*/ /*6*/, (color) and (height) ': None,
            '(color)and(width),(height)': ' (color) and (width), (height) ',
        }
        tests = {}
        for b, a in list(mls.items()):
            if a is None:
                a = b
            tests[f'@media{b}{style}'] = f'@media{a}{style}'

        self.do_equal_p(tests)
        self.do_equal_r(tests)

        tests = {
            '@media only tv{}': '',
            '@media not tv{}': '',
            '@media only tv and (color){}': '',
            '@media only tv and (color: red){}': '',
            '@media only tv and (color: red) and (width: 100px){}': '',
            '@media only tv and (color: red) and (width: 100px), tv{}': '',
            '@media only tv and (color: red) and (width: 100px), tv and (width: 20px){}': '',
            '@media (color: red) and (width: 100px), (width: 20px){}': '',
            '@media (width){}': '',
            '@media (width:10px){}': '',
            '@media (width), (color){}': '',
            '@media (width)  ,  (color),(height){}': '',
            '@media (width)  ,  (color) and (height){}': '',
            '@media (width) and (color){}': '',
            '@media all and (width){}': '',
            '@media all and (width:10px){}': '',
            '@media all and (width), (color){}': '',
            '@media all and (width)  ,  (color),(height){}': '',
            '@media all and (width)  ,  (color) and (height){}': '',
            '@media all and (width) and (color){}': '',
            '@media only tv and (width){}': '',
            '@media only tv and (width:10px){}': '',
            '@media only tv and (width), (color){}': '',
            '@media only tv and (width)  ,  (color),(height){}': '',
            '@media only tv and (width)  ,  (color) and (height){}': '',
            '@media only tv and (width) and (color){}': '',
            '@media only tv and (width) "name" {}': '',
            '@media only tv and (width:10px) "name" {}': '',
            '@media only tv and (width), (color){}': '',
            '@media only tv and (width)  ,  (color),(height){}': '',
            '@media only tv and (width)  ,  (color) and (height){}': '',
            '@media only tv and (width) and (color){}': '',
            '@media all "name"{}': '',
            '@media all {}': '',
            '@media/*x*/all{}': '',
            '@media all { a{ x: 1} }': '@media all {\n    a {\n        x: 1\n        }\n    }',
            '@media all "name" { a{ x: 1} }': '@media all "name" {\n    a {\n        x: 1\n        }\n    }',
            '@MEDIA all { a{x:1} }': '@media all {\n    a {\n        x: 1\n        }\n    }',
            '@\\media all { a{x:1} }': '@media all {\n    a {\n        x: 1\n        }\n    }',
            '@media all {@x some;a{color: red;}b{color: green;}}': '''@media all {
    @x some;
    a {
        color: red
        }
    b {
        color: green
        }
    }''',
            '@media all { @x{}}': '@media all {\n    @x {\n        }\n    }',
            '@media all "n" /**/ { @x{}}': '@media all "n" /**/ {\n    @x {\n        }\n    }',
            # comments
            '@media/*1*//*2*/all/*3*//*4*/{/*5*/a{x:1}}': '@media /*1*/ /*2*/ all /*3*/ /*4*/ {\n    /*5*/\n    a {\n        x: 1\n        }\n    }',
            '@media  /*1*/  /*2*/  all  /*3*/  /*4*/  {  /*5*/  a{ x: 1} }': '@media /*1*/ /*2*/ all /*3*/ /*4*/ {\n    /*5*/\n    a {\n        x: 1\n        }\n    }',
            # WS
            '@media\n\t\f all\n\t\f {\n\t\f a{ x: 1}\n\t\f }': '@media all {\n    a {\n        x: 1\n        }\n    }',
            # @page rule inside @media
            '@media all { @page { margin: 0; } }': '@media all {\n    @page {\n        margin: 0\n        }\n    }',
            # nested media rules
            '@media all { @media all { p { color: red; } } }': '@media all {\n    @media all {\n        p {\n            '
            'color: red\n            }\n        }\n    }',
        }
        self.do_equal_p(tests)
        self.do_equal_r(tests)

        tests = {
            '@media {}': xml.dom.SyntaxErr,
            '@media;': xml.dom.SyntaxErr,
            '@media/*only comment*/{}': xml.dom.SyntaxErr,
            '@media all;': xml.dom.SyntaxErr,
            '@media all "n";': xml.dom.SyntaxErr,
            '@media all; @x{}': xml.dom.SyntaxErr,
            '@media { a{ x: 1} }': xml.dom.SyntaxErr,
            '@media "name" { a{ x: 1} }': xml.dom.SyntaxErr,
            '@media "name" all { a{ x: 1} }': xml.dom.SyntaxErr,
            '@media all { @charset "x"; a{}}': xml.dom.HierarchyRequestErr,
            '@media all { @import "x"; a{}}': xml.dom.HierarchyRequestErr,
            '@media all { , }': xml.dom.SyntaxErr,
            '@media all {}EXTRA': xml.dom.SyntaxErr,
            '@media ({}': xml.dom.SyntaxErr,
            '@media (color{}': xml.dom.SyntaxErr,
            '@media (color:{}': xml.dom.SyntaxErr,
            '@media (color:red{}': xml.dom.SyntaxErr,
            '@media (:red){}': xml.dom.SyntaxErr,
            '@media (:){}': xml.dom.SyntaxErr,
            '@media color:red){}': xml.dom.SyntaxErr,
        }
        self.do_raise_p(tests)
        self.do_raise_r(tests)

        tests = {
            # extra stuff
            '@media all { x{} } a{}': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests)

        m = cssutils.css.CSSMediaRule()
        m.cssText = '''@media all {@x; /*1*/a{color: red;}}'''
        for r in m.cssRules:
            assert m == r.parentRule
            assert m.parentStyleSheet == r.parentStyleSheet

    def test_media(self):
        "CSSMediaRule.media"
        # see CSSImportRule.media

        # setting not allowed
        with pytest.raises(AttributeError):
            self.r.__setattr__('media', None)
        with pytest.raises(AttributeError):
            self.r.__setattr__('media', 0)

        # set mediaText instead
        self.r.media.mediaText = 'print'
        self.r.insertRule(self.stylerule)
        assert '' == self.r.cssText
        cssutils.ser.prefs.keepEmptyRules = True
        assert '@media print {\n    a {}\n    }' == self.r.cssText

    def test_name(self):
        "CSSMediaRule.name"
        r = cssutils.css.CSSMediaRule()
        r.cssText = '@media all "\\n\\"ame" {a{left: 0}}'

        assert '\\n"ame' == r.name
        r.name = "n"
        assert 'n' == r.name
        assert (
            '@media all "n" {\n    a {\n        left: 0\n        }\n    }' == r.cssText
        )
        r.name = '"'
        assert '"' == r.name
        assert (
            '@media all "\\"" {\n    a {\n        left: 0\n        }\n    }'
            == r.cssText
        )

        r.name = ''
        assert r.name is None
        assert '@media all {\n    a {\n        left: 0\n        }\n    }' == r.cssText

        r.name = None
        assert r.name is None
        assert '@media all {\n    a {\n        left: 0\n        }\n    }' == r.cssText

        with pytest.raises(xml.dom.SyntaxErr):
            r._setName(0)
        with pytest.raises(xml.dom.SyntaxErr):
            r._setName(123)

    def test_deleteRuleIndex(self):
        "CSSMediaRule.deleteRule(index)"
        # see CSSStyleSheet.deleteRule
        m = cssutils.css.CSSMediaRule()
        m.cssText = '''@media all {
            @a;
            /* x */
            @b;
            @c;
            @d;
        }'''
        assert 5 == m.cssRules.length
        with pytest.raises(xml.dom.IndexSizeErr):
            m.deleteRule(5)

        # end -1
        # check parentRule
        r = m.cssRules[-1]
        assert m == r.parentRule
        m.deleteRule(-1)
        assert r.parentRule is None

        assert 4 == m.cssRules.length
        assert (
            '@media all {\n    @a;\n    /* x */\n    @b;\n    @c;\n    }' == m.cssText
        )
        # beginning
        m.deleteRule(0)
        assert 3 == m.cssRules.length
        assert '@media all {\n    /* x */\n    @b;\n    @c;\n    }' == m.cssText
        # middle
        m.deleteRule(1)
        assert 2 == m.cssRules.length
        assert '@media all {\n    /* x */\n    @c;\n    }' == m.cssText
        # end
        m.deleteRule(1)
        assert 1 == m.cssRules.length
        assert '@media all {\n    /* x */\n    }' == m.cssText

    def test_deleteRule(self):
        "CSSMediaRule.deleteRule(rule)"
        m = cssutils.css.CSSMediaRule()
        m.cssText = '''@media all {
            a { color: red; }
            b { color: blue; }
            c { color: green; }
        }'''
        s1, s2, s3 = m.cssRules

        r = cssutils.css.CSSStyleRule()
        with pytest.raises(xml.dom.IndexSizeErr):
            m.deleteRule(r)

        assert 3 == m.cssRules.length
        m.deleteRule(s2)
        assert 2 == m.cssRules.length
        assert (
            m.cssText
            == '@media all {\n    a {\n        color: red\n        }\n    c {\n        color: green\n        }\n    }'
        )
        with pytest.raises(xml.dom.IndexSizeErr):
            m.deleteRule(s2)

    def test_add(self):
        "CSSMediaRule.add()"
        # see CSSStyleSheet.add
        r = cssutils.css.CSSMediaRule()
        stylerule1 = cssutils.css.CSSStyleRule()
        stylerule2 = cssutils.css.CSSStyleRule()
        r.add(stylerule1)
        r.add(stylerule2)
        assert r.cssRules[0] == stylerule1
        assert r.cssRules[1] == stylerule2

    def test_insertRule(self):
        "CSSMediaRule.insertRule"
        # see CSSStyleSheet.insertRule
        r = cssutils.css.CSSMediaRule()
        charsetrule = cssutils.css.CSSCharsetRule('ascii')
        importrule = cssutils.css.CSSImportRule('x')
        namespacerule = cssutils.css.CSSNamespaceRule()
        unknownrule = cssutils.css.CSSUnknownRule('@x;')
        stylerule = cssutils.css.CSSStyleRule('a')
        stylerule.cssText = 'a { x: 1}'
        comment1 = cssutils.css.CSSComment('/*1*/')
        comment2 = cssutils.css.CSSComment('/*2*/')

        # hierarchy
        with pytest.raises(xml.dom.HierarchyRequestErr):
            r.insertRule(charsetrule, 0)
        with pytest.raises(xml.dom.HierarchyRequestErr):
            r.insertRule(importrule, 0)
        with pytest.raises(xml.dom.HierarchyRequestErr):
            r.insertRule(namespacerule, 0)

        # start insert
        r.insertRule(stylerule, 0)
        assert r == stylerule.parentRule
        assert r.parentStyleSheet == stylerule.parentStyleSheet
        # before
        r.insertRule(comment1, 0)
        assert r == comment1.parentRule
        assert r.parentStyleSheet == stylerule.parentStyleSheet
        # end explicit
        r.insertRule(unknownrule, 2)
        assert r == unknownrule.parentRule
        assert r.parentStyleSheet == stylerule.parentStyleSheet
        # end implicit
        r.insertRule(comment2)
        assert r == comment2.parentRule
        assert r.parentStyleSheet == stylerule.parentStyleSheet
        assert (
            '@media all {\n    /*1*/\n    a {\n        x: 1\n        }\n    @x;\n    /*2*/\n    }'
            == r.cssText
        )

        # index
        with pytest.raises(xml.dom.IndexSizeErr):
            r.insertRule(stylerule, -1)
        with pytest.raises(xml.dom.IndexSizeErr):
            r.insertRule(stylerule, r.cssRules.length + 1)

    def test_InvalidModificationErr(self):
        "CSSMediaRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr('@media')

    def test_incomplete(self):
        "CSSMediaRule (incomplete)"
        tests = {
            '@media all { @unknown;': '@media all {\n    @unknown;\n    }',  # no }
            '@media all { a {x:"1"}': '@media all {\n    a {\n        x: "1"\n        }\n    }',  # no }
            '@media all { a {x:"1"': '@media all {\n    a {\n        x: "1"\n        }\n    }',  # no }}
            '@media all { a {x:"1': '@media all {\n    a {\n        x: "1"\n        }\n    }',  # no "}}
        }
        self.do_equal_p(tests)  # parse

    def test_reprANDstr(self):
        "CSSMediaRule.__repr__(), .__str__()"
        mediaText = 'tv, print'

        s = cssutils.css.CSSMediaRule(mediaText=mediaText)

        assert mediaText in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert mediaText == s2.media.mediaText
