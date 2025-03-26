"""Tests for css.CSSStyleSheet"""

import xml.dom

import pytest

import cssutils.css

from . import basetest


class TestCSSStyleSheet(basetest.BaseTestCase):
    def setup_method(self):
        self.r = cssutils.css.CSSStyleSheet()  # used by basetest
        self.s = self.r  # used here
        self.rule = cssutils.css.CSSStyleRule()

    def test_init(self):
        "CSSStyleSheet.__init__()"
        assert 'text/css' == self.s.type
        assert not self.s._readonly
        assert [] == self.s.cssRules
        assert not self.s.disabled
        assert self.s.href is None
        assert self.s.media is None
        assert self.s.ownerNode is None
        assert self.s.parentStyleSheet is None
        assert '' == self.s.title

        # check that type is readonly
        with pytest.raises(AttributeError):
            self.r.__setattr__('href', 'x')
        with pytest.raises(AttributeError):
            self.r.__setattr__('parentStyleSheet', 'x')
        with pytest.raises(AttributeError):
            self.r.__setattr__('ownerNode', 'x')
        with pytest.raises(AttributeError):
            self.r.__setattr__('type', 'x')

    def test_iter(self):
        "CSSStyleSheet.__iter__()"
        s = cssutils.css.CSSStyleSheet()
        s.cssText = '''@import "x";@import "y";@namespace "u";'''
        types = [
            cssutils.css.CSSRule.IMPORT_RULE,
            cssutils.css.CSSRule.IMPORT_RULE,
            cssutils.css.CSSRule.NAMESPACE_RULE,
        ]
        for i, rule in enumerate(s):
            assert rule == s.cssRules[i]
            assert rule.type == types[i]

    def test_refs(self):
        """CSSStylesheet references"""
        s = cssutils.parseString('a {}')
        rules = s.cssRules
        assert s.cssRules[0].parentStyleSheet == s
        assert rules[0].parentStyleSheet == s

        # set cssText
        s.cssText = 'b{}'

        # from 0.9.7b1
        assert rules != s.cssRules

        # set cssRules
        s.cssRules = cssutils.parseString(
            '''
            @charset "ascii";
            /**/
            @import "x";
            @namespace "http://example.com/ns0";
            @media all {
                a { color: green; }
                }
            @font-face {
                font-family: x;
                }
            @page {
                font-family: Arial;
                }
            @x;
            b {}').cssRules'''
        ).cssRules
        # new object
        assert rules != s.cssRules
        for r in s.cssRules:
            assert r.parentStyleSheet == s

        # namespaces
        s = cssutils.parseString('@namespace "http://example.com/ns1"; a {}')
        namespaces = s.namespaces
        assert list(s.namespaces.items()) == [('', 'http://example.com/ns1')]
        s.cssText = '@namespace x "http://example.com/ns2"; x|a {}'
        # not anymore!
        assert namespaces != s.namespaces
        assert list(s.namespaces.items()) == [('x', 'http://example.com/ns2')]

        # variables
        s = cssutils.parseString('@variables { a:1}')
        vars1 = s.variables
        assert vars1['a'] == '1'

        s = cssutils.parseString('@variables { a:2}')
        vars2 = s.variables
        assert vars1 != vars2
        assert vars1['a'] == '1'
        assert vars2['a'] == '2'

    def test_cssRules(self):
        "CSSStyleSheet.cssRules"
        s = cssutils.parseString('/*1*/a {x:1}')
        assert 2 == s.cssRules.length
        del s.cssRules[0]
        assert 1 == s.cssRules.length
        s.cssRules.append('/*2*/')
        assert 2 == s.cssRules.length
        s.cssRules.extend(cssutils.parseString('/*3*/x {y:2}').cssRules)
        assert 4 == s.cssRules.length
        assert b'a {\n    x: 1\n    }\n/*2*/\n/*3*/\nx {\n    y: 2\n    }' == s.cssText

        for r in s.cssRules:
            assert r.parentStyleSheet == s

    def test_cssText(self):
        "CSSStyleSheet.cssText"
        tests = {
            '': b'',
            # @charset
            '@charset "ascii";\n@import "x";': b'@charset "ascii";\n@import "x";',
            '@charset "ascii";\n@media all {}': b'@charset "ascii";',
            '@charset "ascii";\n@x;': b'@charset "ascii";\n@x;',
            '@charset "ascii";\na {\n    x: 1\n    }': b'@charset "ascii";\na {\n    x: 1\n    }',
            # @import
            '@x;\n@import "x";': b'@x;\n@import "x";',
            '@import "x";\n@import "y";': b'@import "x";\n@import "y";',
            '@import "x";\n@media all {}': b'@import "x";',
            '@import "x";\n@x;': b'@import "x";\n@x;',
            '@import "x";\na {\n    x: 1\n    }': b'@import "x";\na {\n    x: 1\n    }',
            # @namespace
            '@x;\n@namespace a "x";': b'@x;\n@namespace a "x";',
            '@namespace a "x";\n@namespace b "y";': b'@namespace a "x";\n@namespace b "y";',
            '@import "x";\n@namespace a "x";\n@media all {}': b'@import "x";\n@namespace a "x";',
            '@namespace a "x";\n@x;': b'@namespace a "x";\n@x;',
            '@namespace a "x";\na {\n    x: 1\n    }': b'@namespace a "x";\na {\n    x: 1\n    }',
            """@namespace url("e1");
                @namespace url("e2");
                @namespace x url("x1");
                @namespace x url("x2");
                test{color: green}
                x|test {color: green}""": b"""@namespace "e2";
@namespace x "x2";
test {
    color: green
    }
x|test {
    color: green
    }""",
            #            ur'\1 { \2: \3 }': ur'''\x01 {
            #    \x02: \x03
            #    }''',
            #            ur'''
            #            \@ { \@: \@ }
            #            \1 { \2: \3 }
            #            \{{\::\;;}
            #            ''': ur'''\@ {
            #    \@: \@
            #    }
            # \1 {
            #    \2: \3
            #    }
            # \{
            #    {\:: \;
            #    }'''
        }
        self.do_equal_r(tests)

        tests = {
            '': None,
            # @charset
            '@charset "ascii";\n@import "x";': None,
            '@charset "ascii";\n@media all {}': '@charset "ascii";',
            '@charset "ascii";\n@x;': None,
            '@charset "ascii";\na {\n    x: 1\n    }': None,
            # @import
            '@x;\n@import "x";': None,
            '@import "x";\n@import "y";': None,
            '@import "x";\n@media all {}': '@import "x";',
            '@import "x";\n@x;': None,
            '@import "x";\na {\n    x: 1\n    }': None,
            # @namespace
            '@x;\n@namespace a "x";': None,
            '@namespace a "x";\n@namespace b "y";': None,
            '@import "x";\n@namespace a "x";\n@media all {}': '@import "x";\n@namespace a "x";',
            '@namespace a "x";\n@x;': None,
            '@namespace a "x";\na {\n    x: 1\n    }': None,
            """@namespace url("e1");
                @namespace url("e2");
                @namespace x url("x1");
                @namespace x url("x2");
                test{color: green}
                x|test {color: green}""": """@namespace "e2";
@namespace x "x2";
test {
    color: green
    }
x|test {
    color: green
    }""",
            #            ur'\1 { \2: \3 }': ur'''\x01 {
            #    \x02: \x03
            #    }''',
            #            ur'''
            #            \@ { \@: \@ }
            #            \1 { \2: \3 }
            #            \{{\::\;;}
            #            ''': ur'''\@ {
            #    \@: \@
            #    }
            # \1 {
            #    \2: \3
            #    }
            # \{
            #    {\:: \;
            #    }'''
        }
        self.do_equal_p(tests)

        s = cssutils.css.CSSStyleSheet()
        s.cssText = '''@charset "ascii";@import "x";@namespace a "x";
        @media all {/*1*/}@page {margin: 0}a {\n    x: 1\n    }@unknown;/*comment*/'''
        for r in s.cssRules:
            assert s == r.parentStyleSheet

    def test_cssText_HierarchyRequestErr(self):
        "CSSStyleSheet.cssText HierarchyRequestErr"
        tests = {
            # @charset: only one and always 1st
            ' @charset "utf-8";': xml.dom.HierarchyRequestErr,
            '@charset "ascii";@charset "ascii";': xml.dom.HierarchyRequestErr,
            '/*c*/@charset "ascii";': xml.dom.HierarchyRequestErr,
            '@import "x"; @charset "ascii";': xml.dom.HierarchyRequestErr,
            '@namespace a "x"; @charset "ascii";': xml.dom.HierarchyRequestErr,
            '@media all {} @charset "ascii";': xml.dom.HierarchyRequestErr,
            '@page {} @charset "ascii";': xml.dom.HierarchyRequestErr,
            'a {} @charset "ascii";': xml.dom.HierarchyRequestErr,
            # @import: before @namespace, @media, @page, sr
            '@namespace a "x"; @import "x";': xml.dom.HierarchyRequestErr,
            '@media all {} @import "x";': xml.dom.HierarchyRequestErr,
            '@page {} @import "x";': xml.dom.HierarchyRequestErr,
            'a {} @import "x";': xml.dom.HierarchyRequestErr,
            # @namespace: before @media, @page, sr
            '@media all {} @namespace a "x";': xml.dom.HierarchyRequestErr,
            '@page {} @namespace a "x";': xml.dom.HierarchyRequestErr,
            'a {} @namespace a "x";': xml.dom.HierarchyRequestErr,
        }
        self.do_raise_r(tests)
        self.do_raise_p(tests)

    def test_cssText_SyntaxErr(self):
        """CSSStyleSheet.cssText SyntaxErr

        for single {, } or ;
        """
        tests = {
            '{': xml.dom.SyntaxErr,
            '}': xml.dom.SyntaxErr,
            ';': xml.dom.SyntaxErr,
            '@charset "ascii";{': xml.dom.SyntaxErr,
            '@charset "ascii";}': xml.dom.SyntaxErr,
            '@charset "ascii";;': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests)
        self.do_raise_p(tests)

    def test_encoding(self):
        "CSSStyleSheet.encoding"
        self.s.cssText = ''
        assert 'utf-8' == self.s.encoding

        self.s.encoding = 'ascii'
        assert 'ascii' == self.s.encoding
        assert 1 == self.s.cssRules.length
        assert 'ascii' == self.s.cssRules[0].encoding

        self.s.encoding = None
        assert 'utf-8' == self.s.encoding
        assert 0 == self.s.cssRules.length

        self.s.encoding = 'UTF-8'
        assert 'utf-8' == self.s.encoding
        assert 1 == self.s.cssRules.length

        with pytest.raises(xml.dom.SyntaxErr):
            self.s._setEncoding('INVALID ENCODING')
        assert 'utf-8' == self.s.encoding
        assert 1 == self.s.cssRules.length

    def test_namespaces1(self):
        "CSSStyleSheet.namespaces.namespaces"
        # tests for namespaces internal methods
        s = cssutils.css.CSSStyleSheet()
        assert 0 == len(s.namespaces)

        css = '''@namespace "default";
@namespace ex "example";
@namespace ex2 "example";
ex2|x { top: 0 }'''
        expcss = '''@namespace "default";
@namespace ex2 "example";
ex2|x {
    top: 0
    }'''
        s.cssText = css
        assert s.cssText == expcss.encode()
        assert s.namespaces.namespaces == {'': 'default', 'ex2': 'example'}

        # __contains__
        assert '' in s.namespaces
        assert 'ex2' in s.namespaces
        assert "NOTSET" not in s.namespaces
        # __delitem__
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            s.namespaces.__delitem__('ex2')
        s.namespaces['del'] = 'del'
        del s.namespaces['del']
        with pytest.raises(xml.dom.NamespaceErr):
            s.namespaces.__getitem__('del')
        # __getitem__
        assert 'default' == s.namespaces['']
        assert 'example' == s.namespaces['ex2']
        with pytest.raises(xml.dom.NamespaceErr):
            s.namespaces.__getitem__('UNSET')
        # __iter__
        assert ['', 'ex2'] == sorted(list(s.namespaces))
        # __len__
        assert 2 == len(s.namespaces)
        # __setitem__
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            s.namespaces.__setitem__('ex2', 'NEWURI')
        s.namespaces['n1'] = 'new'
        assert s.namespaces.namespaces == {'': 'default', 'ex2': 'example', 'n1': 'new'}
        s.namespaces['n'] = 'new'  # replaces prefix!
        assert s.namespaces.namespaces == {'': 'default', 'ex2': 'example', 'n': 'new'}
        # prefixForNamespaceURI
        assert '' == s.namespaces.prefixForNamespaceURI('default')
        assert 'ex2' == s.namespaces.prefixForNamespaceURI('example')
        with pytest.raises(IndexError):
            s.namespaces.prefixForNamespaceURI('UNSET')
        # .keys
        assert set(s.namespaces.keys()) == {'', 'ex2', 'n'}
        # .get
        assert 'x' == s.namespaces.get('UNKNOWN', 'x')
        assert 'example' == s.namespaces.get('ex2', 'not used defa')

    def test_namespaces2(self):
        "CSSStyleSheet.namespaces"
        # tests using CSSStyleSheet.namespaces

        s = cssutils.css.CSSStyleSheet()
        css = '@namespace n "new";'
        # doubles will be removed
        s.insertRule(css + css)
        assert s.cssText == css.encode()
        r = cssutils.css.CSSNamespaceRule(prefix='ex2', namespaceURI='example')
        s.insertRule(r)
        r = cssutils.css.CSSNamespaceRule(namespaceURI='default')
        s.insertRule(r)

        expcss = '''@namespace n "new";
@namespace ex2 "example";
@namespace "default";'''
        assert s.cssText == expcss.encode()
        r.prefix = 'DEFAULT'
        expcss = '''@namespace n "new";
@namespace ex2 "example";
@namespace DEFAULT "default";'''
        assert s.cssText == expcss.encode()

        # CSSMediaRule
        with pytest.raises(xml.dom.NamespaceErr):
            s.add('@media all {x|a {left: 0}}')
        mcss = '@media all {\n    ex2|SEL1 {\n        left: 0\n        }\n    }'
        s.add(mcss)
        expcss += '\n' + mcss
        assert s.cssText == expcss.encode()

        # CSSStyleRule
        with pytest.raises(xml.dom.NamespaceErr):
            s.add('x|a {top: 0}')
        scss = 'n|SEL2 {\n    top: 0\n    }'
        s.add(scss)
        expcss += '\n' + scss
        assert s.cssText == expcss.encode()

        mr = s.cssRules[3]
        sr = s.cssRules[4]

        # SelectorList @media
        with pytest.raises(xml.dom.NamespaceErr):
            mr.cssRules[0]._setSelectorText('x|b')
        oldsel, newsel = mr.cssRules[0].selectorText, 'n|SEL3, a'
        mr.cssRules[0].selectorText = newsel
        expcss = expcss.replace(oldsel, newsel)
        assert s.cssText == expcss.encode()
        # SelectorList stylerule
        with pytest.raises(xml.dom.NamespaceErr):
            sr._setSelectorText('x|b')
        oldsel, newsel = sr.selectorText, 'ex2|SEL4, a'
        sr.selectorText = newsel
        expcss = expcss.replace(oldsel, newsel)
        assert s.cssText == expcss.encode()

        # Selector @media
        with pytest.raises(xml.dom.NamespaceErr):
            mr.cssRules[0].selectorList.append('x|b')
        oldsel, newsel = mr.cssRules[0].selectorText, 'ex2|SELMR'
        mr.cssRules[0].selectorList.append(newsel)
        expcss = expcss.replace(oldsel, oldsel + ', ' + newsel)
        assert s.cssText == expcss.encode()
        # Selector stylerule
        with pytest.raises(xml.dom.NamespaceErr):
            sr.selectorList.append('x|b')
        oldsel, newsel = sr.selectorText, 'ex2|SELSR'
        sr.selectorList.append(newsel)
        expcss = expcss.replace(oldsel, oldsel + ', ' + newsel)
        assert s.cssText == expcss.encode()

        assert (
            s.cssText
            == b'''@namespace n "new";
@namespace ex2 "example";
@namespace DEFAULT "default";
@media all {
    n|SEL3, a, ex2|SELMR {
        left: 0
        }
    }
ex2|SEL4, a, ex2|SELSR {
    top: 0
    }'''
        )

    def test_namespaces3(self):
        "CSSStyleSheet.namespaces 3"
        # tests setting namespaces with new {}
        s = cssutils.css.CSSStyleSheet()
        css = 'h|a { top: 0 }'
        with pytest.raises(xml.dom.NamespaceErr):
            s.add(css)

        s.add('@namespace x "html";')
        assert s.namespaces['x'] == 'html'

        r = cssutils.css.CSSStyleRule()
        r.cssText = (css, {'h': 'html'})
        s.add(r)  # uses x as set before! h is temporary only
        assert s.cssText == b'@namespace x "html";\nx|a {\n    top: 0\n    }'

        # prefix is now "x"!
        with pytest.raises(xml.dom.NamespaceErr):
            r.selectorList.append('h|b')
        with pytest.raises(xml.dom.NamespaceErr):
            r.selectorList.append('y|b')
        s.namespaces['y'] = 'html'
        r.selectorList.append('y|b')
        assert s.cssText == b'@namespace y "html";\ny|a, y|b {\n    top: 0\n    }'

        with pytest.raises(xml.dom.NoModificationAllowedErr):
            s.namespaces.__delitem__('y')
        assert s.cssText == b'@namespace y "html";\ny|a, y|b {\n    top: 0\n    }'

        s.cssRules[0].prefix = ''
        assert s.cssText == b'@namespace "html";\na, b {\n    top: 0\n    }'

        # remove need of namespace
        s.cssRules[0].prefix = 'x'
        s.cssRules[1].selectorText = 'a, b'
        assert s.cssText == b'@namespace x "html";\na, b {\n    top: 0\n    }'

    def test_namespaces4(self):
        "CSSStyleSheet.namespaces 4"
        # tests setting namespaces with new {}
        s = cssutils.css.CSSStyleSheet()
        assert {} == s.namespaces.namespaces

        s.namespaces.namespaces['a'] = 'no setting possible'
        assert {} == s.namespaces.namespaces

        s.namespaces[None] = 'default'
        assert {'': 'default'} == s.namespaces.namespaces

        del s.namespaces['']
        assert {} == s.namespaces.namespaces

        s.namespaces[''] = 'default'
        assert {'': 'default'} == s.namespaces.namespaces

        del s.namespaces[None]
        assert {} == s.namespaces.namespaces

        s.namespaces['p'] = 'uri'
        # cannot use namespaces.namespaces
        del s.namespaces.namespaces['p']
        assert {'p': 'uri'} == s.namespaces.namespaces

        with pytest.raises(xml.dom.NamespaceErr, match=r"Prefix undefined not found\."):
            del s.namespaces['undefined']

    def test_namespaces5(self):
        "CSSStyleSheet.namespaces 5"
        # unknown namespace
        s = cssutils.parseString('a|a { color: red }')
        assert s.cssText == b''

        s = cssutils.css.CSSStyleSheet()
        with pytest.raises(xml.dom.NamespaceErr, match=r"Prefix a not found\."):
            s._setCssText('a|a { color: red }')

    def test_deleteRuleIndex(self):
        "CSSStyleSheet.deleteRule(index)"
        self.s.cssText = '@charset "ascii"; @import "x"; @x; a {\n    x: 1\n    }@y;'
        assert 5 == self.s.cssRules.length

        with pytest.raises(xml.dom.IndexSizeErr):
            self.s.deleteRule(5)

        # end -1
        # check parentStyleSheet
        r = self.s.cssRules[-1]
        assert self.s == r.parentStyleSheet
        self.s.deleteRule(-1)
        assert r.parentStyleSheet is None

        assert 4 == self.s.cssRules.length
        assert (
            b'@charset "ascii";\n@import "x";\n@x;\na {\n    x: 1\n    }'
            == self.s.cssText
        )
        # beginning
        self.s.deleteRule(0)
        assert 3 == self.s.cssRules.length
        assert b'@import "x";\n@x;\na {\n    x: 1\n    }' == self.s.cssText
        # middle
        self.s.deleteRule(1)
        assert 2 == self.s.cssRules.length
        assert b'@import "x";\na {\n    x: 1\n    }' == self.s.cssText
        # end
        self.s.deleteRule(1)
        assert 1 == self.s.cssRules.length
        assert b'@import "x";' == self.s.cssText

    def test_deleteRule(self):
        "CSSStyleSheet.deleteRule(rule)"
        s = cssutils.css.CSSStyleSheet()
        s.cssText = '''
        @namespace x "http://example.com";
        a { color: red; }
        b { color: blue; }
        c { color: green; }
        '''
        n, s1, s2, s3 = s.cssRules

        r = cssutils.css.CSSStyleRule()
        with pytest.raises(xml.dom.IndexSizeErr):
            s.deleteRule(r)

        assert 4 == s.cssRules.length
        s.deleteRule(n)
        assert 3 == s.cssRules.length
        assert (
            s.cssText
            == b'a {\n    color: red\n    }\nb {\n    color: blue\n    }\nc {\n    color: green\n    }'
        )
        with pytest.raises(xml.dom.IndexSizeErr):
            s.deleteRule(n)
        s.deleteRule(s2)
        assert 2 == s.cssRules.length
        assert s.cssText == b'a {\n    color: red\n    }\nc {\n    color: green\n    }'
        with pytest.raises(xml.dom.IndexSizeErr):
            s.deleteRule(s2)

    def _gets(self):
        # complete
        self.cr = cssutils.css.CSSCharsetRule('ascii')
        self.c = cssutils.css.CSSComment('/*c*/')
        self.ur = cssutils.css.CSSUnknownRule('@x;')
        self.ir = cssutils.css.CSSImportRule('x')
        self.nr = cssutils.css.CSSNamespaceRule('uri', 'p')
        self.mr = cssutils.css.CSSMediaRule()
        self.mr.cssText = '@media all { @m; }'
        self.pr = cssutils.css.CSSPageRule()
        self.pr.style = 'margin: 0;'
        self.sr = cssutils.css.CSSStyleRule()
        self.sr.cssText = 'a {\n    x: 1\n    }'

        s = cssutils.css.CSSStyleSheet()
        s.insertRule(self.cr)  # 0
        s.insertRule(self.ir)  # 1
        s.insertRule(self.nr)  # 2
        s.insertRule(self.mr)  # 3
        s.insertRule(self.sr)  # 4
        s.insertRule(self.mr)  # 5
        s.insertRule(self.pr)  # 6
        s.insertRule(self.sr)  # 7
        assert (
            b'@charset "ascii";\n@import url(x);\n@namespace p "uri";\n@media all {\n    @m;\n    }\na {\n    x: 1\n    }\n@media all {\n    @m;\n    }\n@page {\n    margin: 0\n    }\na {\n    x: 1\n    }'
            == s.cssText
        )
        return s, s.cssRules.length

    def test_add(self):
        "CSSStyleSheet.add()"
        full = cssutils.css.CSSStyleSheet()
        sheet = cssutils.css.CSSStyleSheet()
        css = [
            '@charset "ascii";',
            '@import "x";',
            '@namespace p "u";',
            '@page {\n    left: 0\n    }',
            '@font-face {\n    src: local(x)\n    }',
            '@media all {\n    a {\n        color: red\n        }\n    }',
            'a {\n    color: green\n    }',
            '/*comment*/',
            '@x;',
        ]

        fullcss = '\n'.join(css)
        full.cssText = fullcss
        assert full.cssText == fullcss.encode()
        for i, line in enumerate(css):
            # sheet without same ruletype
            before = css[:i]
            after = css[i + 1 :]
            sheet.cssText = ''.join(before + after)

            index = sheet.add(line)
            if i < 3:
                # specific insertion point
                assert fullcss.encode() == sheet.cssText
                assert i == index
            else:
                # end of sheet
                expected = before
                expected.extend(after)
                expected.append(line)
                assert '\n'.join(expected).encode() == sheet.cssText
                assert len(expected) - 1 == index  # no same rule present

            # sheet with the same ruletype
            if i == 1:
                line = '@import "x2";'
            if i == 2:
                line = '@namespace p2 "u2";'

            full.cssText = fullcss
            index = full.add(line)
            if i < 1:
                assert fullcss.encode() == sheet.cssText
                assert i == index  # no same rule present
            else:
                if i < 3:
                    # in order
                    expected = css[: i + 1]  # including same rule
                    expected.append(line)
                    expected.extend(css[i + 1 :])
                    expectedindex = i + 1
                else:
                    # just appended as no order needed
                    expected = css[:]
                    expected.append(line)
                    expectedindex = len(expected) - 1

                assert '\n'.join(expected).encode() == full.cssText
                assert expectedindex == index  # no same rule present

    def test_addimport(self):
        p = cssutils.CSSParser(fetcher=lambda url: (None, '/**/'))

        cssrulessheet = p.parseString('@import "example.css";')
        imports = (
            '@import "example.css";',  # string
            cssutils.css.CSSImportRule(href="example.css"),  # CSSRule
            cssrulessheet.cssRules,  # CSSRuleList
        )
        for imp in imports:
            sheet = p.parseString('', href='http://example.com')
            sheet.add(imp)
            added = sheet.cssRules[0]
            assert sheet == added.parentStyleSheet
            assert 'example.css' == added.href
            assert 'utf-8' == added.styleSheet.encoding
            assert b'/**/' == added.styleSheet.cssText

        cssrulessheet = p.parseString('@import "example.css";')
        imports = (
            ('@import "example.css";', 'ascii'),  # string
            (cssutils.css.CSSImportRule(href="example.css"), 'ascii'),  # CSSRule
            # got encoding from old parent already
            (cssrulessheet.cssRules, 'utf-8'),  # CSSRuleList
        )
        for imp, enc in imports:
            sheet = p.parseString('', href='http://example.com', encoding='ascii')
            sheet.add(imp)
            added = sheet.cssRules[1]
            assert sheet == added.parentStyleSheet
            assert 'example.css' == added.href
            assert enc == added.styleSheet.encoding
            if enc == 'ascii':
                assert b'@charset "ascii";\n/**/' == added.styleSheet.cssText
            else:
                assert b'/**/' == added.styleSheet.cssText

        # if styleSheet is already there encoding is not set new
        impsheet = p.parseString('@import "example.css";')
        imp = impsheet.cssRules[0]
        sheet = p.parseString('', href='http://example.com', encoding='ascii')
        sheet.add(imp)
        added = sheet.cssRules[1]
        assert sheet == added.parentStyleSheet
        assert 'example.css' == added.href
        assert 'utf-8' == added.styleSheet.encoding
        assert b'/**/' == added.styleSheet.cssText

    def test_insertRule(self):
        "CSSStyleSheet.insertRule()"
        s, L = self._gets()

        # INVALID index
        with pytest.raises(xml.dom.IndexSizeErr):
            s.insertRule(self.sr, -1)
        with pytest.raises(xml.dom.IndexSizeErr):
            s.insertRule(self.sr, s.cssRules.length + 1)
        #   check if rule is really not in
        assert L == s.cssRules.length

        # insert string
        s.insertRule('a {}')
        assert L + 1 == s.cssRules.length
        # insert rule
        s.insertRule(self.sr)
        assert L + 2 == s.cssRules.length
        # insert rulelist
        s2, L2 = self._gets()
        rulelist = s2.cssRules
        del rulelist[:-2]
        s.insertRule(rulelist)
        assert L + 2 + 2 == s.cssRules.length

    def _insertRule(self, rules, notbefore, notafter, anywhere, checkdoubles=True):
        """
        helper
        test if any rule in rules cannot be inserted before rules in before
        or after rules in after but before and after rules in anywhere
        """
        for rule in rules:
            for r in notbefore:
                s = cssutils.css.CSSStyleSheet()
                s.insertRule(r)
                with pytest.raises(xml.dom.HierarchyRequestErr):
                    s.insertRule(rule, 0)
                s = cssutils.css.CSSStyleSheet()
                s.add(r)
                with pytest.raises(xml.dom.HierarchyRequestErr):
                    s.insertRule(rule, 0)
            for r in notafter:
                s = cssutils.css.CSSStyleSheet()
                s.insertRule(r)
                with pytest.raises(xml.dom.HierarchyRequestErr):
                    s.insertRule(rule, 1)
                s = cssutils.css.CSSStyleSheet()
                s.add(r)
                s.add(rule)  # never raises
                assert s == r.parentStyleSheet

            for r in anywhere:
                s = cssutils.css.CSSStyleSheet()
                s.insertRule(r)
                s.insertRule(rule, 0)  # before
                s.insertRule(rule)  # after
                if checkdoubles:
                    assert s.cssRules.length == 3
                assert s == r.parentStyleSheet

    def test_insertRule_charset(self):
        "CSSStyleSheet.insertRule(@charset)"
        s, L = self._gets()
        notbefore = (self.cr,)
        notafter = (
            self.cr,
            self.ir,
            self.nr,
            self.mr,
            self.pr,
            self.sr,
            self.c,
            self.ur,
        )
        anywhere = ()
        self._insertRule((self.cr,), notbefore, notafter, anywhere)

    def test_insertRule_import(self):
        "CSSStyleSheet.insertRule(@import)"
        s, L = self._gets()
        notbefore = (self.cr,)
        notafter = (self.nr, self.pr, self.mr, self.sr)
        anywhere = (self.c, self.ur, self.ir)
        self._insertRule((self.ir,), notbefore, notafter, anywhere)

    def test_insertRule_namespace(self):
        "CSSStyleSheet.insertRule(@namespace)"
        s, L = self._gets()
        notbefore = (self.cr, self.ir)
        notafter = (self.pr, self.mr, self.sr)
        anywhere = (self.c, self.ur, self.nr)
        self._insertRule((self.nr,), notbefore, notafter, anywhere, checkdoubles=False)

    def test_insertRule_media_page_style(self):
        "CSSStyleSheet.insertRule(@media, @page, stylerule)"
        s, L = self._gets()
        notbefore = (self.cr, self.ir, self.nr)
        notafter = ()
        anywhere = (self.c, self.ur, self.mr, self.pr, self.sr)
        self._insertRule((self.pr, self.mr, self.sr), notbefore, notafter, anywhere)

    def test_insertRule_unknownandcomment(self):
        "CSSStyleSheet.insertRule(@ unknown, comment)"
        s, L = self._gets()
        notbefore = (self.cr,)
        notafter = ()
        anywhere = (self.c, self.ur, self.ir, self.nr, self.mr, self.pr, self.sr)
        self._insertRule((self.ur,), notbefore, notafter, anywhere)

    def test_HTMLComments(self):
        "CSSStyleSheet CDO CDC"
        css = '''body { color: red }
<!-- comment -->
body { color: blue }
body { color: pink }
<!-- comment -->
body { color: green }
'''
        exp = '''body {
    color: red
    }
body {
    color: pink
    }'''
        sheet = cssutils.parseString(css)
        assert sheet.cssText == exp.encode()

    def test_incomplete(self):
        "CSSStyleRule (incomplete)"
        tests = {
            '@import "a': '@import "a";',  # no }
            'a { x: 1': 'a {\n    x: 1\n    }',  # no }
            'a { font-family: "arial sans': 'a {\n    font-family: "arial sans"\n    }',  # no "
        }
        self.do_equal_p(tests)  # parse

    def test_NoModificationAllowedErr(self):
        "CSSStyleSheet NoModificationAllowedErr"
        css = cssutils.css.CSSStyleSheet(readonly=True)

        assert css._readonly  # internal...

        with pytest.raises(xml.dom.NoModificationAllowedErr):
            css._setCssText('@x;')
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            css.insertRule(self.rule)
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            css.insertRule(self.rule, 0)
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            css.deleteRule(0)

    def test_reprANDstr(self):
        "CSSStyleSheet.__repr__(), .__str__()"
        href = 'file:foo.css'
        title = 'title-of-css'

        s = cssutils.css.CSSStyleSheet(href=href, title=title)

        assert href in str(s)
        assert title in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert href == s2.href
        assert title == s2.title

    def test_valid(self):
        cases = [
            ('body { color: red; }', True),
            ('body { color: asd; }', False),
            ('body { foo: 12px; }', False),
        ]
        for case, expected in cases:
            sheet = cssutils.parseString(case)
            msg = "{!r} should be {}".format(case, 'valid' if expected else 'invalid')
            assert sheet.valid == expected, msg
