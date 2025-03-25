"""Testcases for cssutils.css.cssvariablesdelaration.CSSVariablesDeclaration."""

import xml.dom

import cssutils

from . import basetest


class TestCSSVariablesDeclaration(basetest.BaseTestCase):
    def setup_method(self):
        self.r = cssutils.css.CSSVariablesDeclaration()

    def test_init(self):
        "CSSVariablesDeclaration.__init__()"
        v = cssutils.css.CSSVariablesDeclaration()
        assert '' == v.cssText
        assert 0 == v.length
        assert v.parentRule is None

        v = cssutils.css.CSSVariablesDeclaration(cssText='x: 0')
        assert 'x: 0' == v.cssText
        assert '0' == v.getVariableValue('x')

        rule = cssutils.css.CSSVariablesRule()
        v = cssutils.css.CSSVariablesDeclaration(cssText='x: 0', parentRule=rule)
        assert rule == v.parentRule

    def test__contains__(self):
        "CSSVariablesDeclaration.__contains__(name)"
        v = cssutils.css.CSSVariablesDeclaration(cssText='x: 0; y: 2')
        for test in ('x', 'y'):
            assert test in v
            assert test.upper() in v

        assert 'z' not in v

    def test_items(self):
        "CSSVariablesDeclaration[variableName]"
        v = cssutils.css.CSSVariablesDeclaration()

        value = '0'
        v['X'] = value
        assert value == v['X']
        assert value == v.getVariableValue('X')
        assert value == v['x']
        assert value == v.getVariableValue('x')

        assert '' == v['y']
        assert '' == v.getVariableValue('y')

        v['z'] = '1'
        assert 2 == v.length

        # unsorted!
        assert sorted(v) == ['x', 'z']

        del v['z']
        assert 1 == v.length
        assert 1 == v.length

        assert '0' == v.removeVariable('x')
        assert '' == v.removeVariable('z')
        assert 0 == v.length

        v.cssText = 'x:0; y:1'
        keys = []
        # unsorted!
        for i in range(0, v.length):
            keys.append(v.item(i))
        assert sorted(keys) == ['x', 'y']

    def test_keys(self):
        "CSSVariablesDeclaration.keys()"
        v = cssutils.css.CSSVariablesDeclaration(cssText='x: 0; Y: 2')
        assert ['x', 'y'] == sorted(v.keys())

    def test_cssText(self):
        "CSSVariablesDeclaration.cssText"
        # empty
        tests = {
            '': '',
            ' ': '',
            ' \t \n  ': '',
            'x: 1': None,
            'x: "a"': None,
            'x: rgb(1, 2, 3)': None,
            'x: 1px 2px 3px': None,
            'x:1': 'x: 1',
            'x:1;': 'x: 1',
            'x  :  1  ': 'x: 1',
            'x  :  1  ;  ': 'x: 1',
            'x:1;y:2': 'x: 1;\ny: 2',
            'x:1;y:2;': 'x: 1;\ny: 2',
            'x  :  1  ;  y  :  2  ': 'x: 1;\ny: 2',
            'x  :  1  ;  y  :  2  ;  ': 'x: 1;\ny: 2',
            '/*x*/': '/*x*/',
            'x555: 5': None,
            'xxx:1;yyy:2': 'xxx: 1;\nyyy: 2',
            'xxx : 1; yyy : 2': 'xxx: 1;\nyyy: 2',
            'x:1;x:2;X:2': 'x: 2',
            'same:1;SAME:2;': 'same: 2',
            '/**/x/**/:/**/1/**/;/**/y/**/:/**/2/**/': '/**/ \n /**/ \n /**/ \n x: 1 /**/;\n/**/ \n /**/ \n /**/ \n y: 2 /**/',
        }
        self.do_equal_r(tests)

        def test_cssText2(self):
            "CSSVariablesDeclaration.cssText"

            tests = {
                'top': xml.dom.SyntaxErr,
                'top:': xml.dom.SyntaxErr,
                'top : ': xml.dom.SyntaxErr,
                'top:;': xml.dom.SyntaxErr,
                'top 0': xml.dom.SyntaxErr,
                'top 0;': xml.dom.SyntaxErr,
                ':': xml.dom.SyntaxErr,
                ':0': xml.dom.SyntaxErr,
                ':0;': xml.dom.SyntaxErr,
                ':;': xml.dom.SyntaxErr,
                ': ;': xml.dom.SyntaxErr,
                '0': xml.dom.SyntaxErr,
                '0;': xml.dom.SyntaxErr,
                ';': xml.dom.SyntaxErr,
            }
            self.do_raise_r(tests)

    def test_xVariable(self):
        "CSSVariablesDeclaration.xVariable()"
        v = cssutils.css.CSSVariablesDeclaration()
        # unset
        assert '' == v.getVariableValue('x')
        # set
        v.setVariable('x', '0')
        assert '0' == v.getVariableValue('x')
        assert '0' == v.getVariableValue('X')
        assert 'x: 0' == v.cssText
        v.setVariable('X', '0')
        assert '0' == v.getVariableValue('x')
        assert '0' == v.getVariableValue('X')
        assert 'x: 0' == v.cssText
        # remove
        assert '0' == v.removeVariable('x')
        assert '' == v.removeVariable('x')
        assert '' == v.getVariableValue('x')
        assert '' == v.cssText

    def test_imports(self):
        "CSSVariables imports"

        def fetcher(url):
            url = url.replace('\\', '/')
            url = url[url.rfind('/') + 1 :]
            return (
                None,
                {
                    '3.css': '''
                    @variables {
                        over3-2-1-0: 3;
                        over3-2-1: 3;
                        over3-2: 3;
                        over3-2-0: 3;
                        over3-1: 3;
                        over3-1-0: 3;
                        over3-0: 3;
                        local3: 3;
                    }

                ''',
                    '2.css': '''
                    @variables {
                        over3-2-1-0: 2;
                        over3-2-1: 2;
                        over3-2-0: 2;
                        over3-2: 2;
                        over2-1: 2;
                        over2-1-0: 2;
                        over2-0: 2;
                        local2: 2;
                    }

                ''',
                    '1.css': '''
                    @import "3.css";
                    @import "2.css";
                    @variables {
                        over3-2-1-0: 1;
                        over3-2-1: 1;
                        over3-1: 1;
                        over3-1-0: 1;
                        over2-1: 1;
                        over2-1-0: 1;
                        over1-0: 1;
                        local1: 1;
                    }

                ''',
                }[url],
            )

        css = '''
            @import "1.css";
            @variables {
                over3-2-1-0: 0;
                over3-2-0: 0;
                over3-1-0: 0;
                over2-1-0: 0;
                over3-0: 0;
                over2-0: 0;
                over1-0: 0;
                local0: 0;
            }
            a {
                local0: var(local0);
                local1: var(local1);
                local2: var(local2);
                local3: var(local3);
                over1-0: var(over1-0);
                over2-0: var(over2-0);
                over3-0: var(over3-0);
                over2-1: var(over2-1);
                over3-1: var(over3-1);
                over3-2: var(over3-2);
                over2-1-0: var(over2-1-0);
                over3-2-0: var(over3-2-0);
                over3-2-1: var(over3-2-1);
                over3-2-1-0: var(over3-2-1-0);
            }
        '''
        p = cssutils.CSSParser(fetcher=fetcher)
        s = p.parseString(css)

        # only these in rule of this sheet
        assert s.cssRules[1].variables.length == 8
        # but all vars in s available!
        assert s.variables.length == 15
        assert [
            'local0',
            'local1',
            'local2',
            'local3',
            'over1-0',
            'over2-0',
            'over2-1',
            'over2-1-0',
            'over3-0',
            'over3-1',
            'over3-1-0',
            'over3-2',
            'over3-2-0',
            'over3-2-1',
            'over3-2-1-0',
        ] == sorted(s.variables.keys())

        # test with variables rule
        cssutils.ser.prefs.resolveVariables = False
        assert (
            s.cssText
            == b'''@import "1.css";
@variables {
    over3-2-1-0: 0;
    over3-2-0: 0;
    over3-1-0: 0;
    over2-1-0: 0;
    over3-0: 0;
    over2-0: 0;
    over1-0: 0;
    local0: 0
    }
a {
    local0: var(local0);
    local1: var(local1);
    local2: var(local2);
    local3: var(local3);
    over1-0: var(over1-0);
    over2-0: var(over2-0);
    over3-0: var(over3-0);
    over2-1: var(over2-1);
    over3-1: var(over3-1);
    over3-2: var(over3-2);
    over2-1-0: var(over2-1-0);
    over3-2-0: var(over3-2-0);
    over3-2-1: var(over3-2-1);
    over3-2-1-0: var(over3-2-1-0)
    }'''
        )

        # test with resolved vars
        cssutils.ser.prefs.resolveVariables = True
        assert (
            s.cssText
            == b'''@import "1.css";
a {
    local0: 0;
    local1: 1;
    local2: 2;
    local3: 3;
    over1-0: 0;
    over2-0: 0;
    over3-0: 0;
    over2-1: 1;
    over3-1: 1;
    over3-2: 2;
    over2-1-0: 0;
    over3-2-0: 0;
    over3-2-1: 1;
    over3-2-1-0: 0
    }'''
        )

        s = cssutils.resolveImports(s)
        assert (
            s.cssText
            == b'''/* START @import "1.css" */
/* START @import "3.css" */
/* START @import "2.css" */
a {
    local0: 0;
    local1: 1;
    local2: 2;
    local3: 3;
    over1-0: 0;
    over2-0: 0;
    over3-0: 0;
    over2-1: 1;
    over3-1: 1;
    over3-2: 2;
    over2-1-0: 0;
    over3-2-0: 0;
    over3-2-1: 1;
    over3-2-1-0: 0
    }'''
        )

    def test_parentRule(self):
        "CSSVariablesDeclaration.parentRule"
        s = cssutils.parseString('@variables { a:1}')
        r = s.cssRules[0]
        d = r.variables
        assert r == d.parentRule

        d2 = cssutils.css.CSSVariablesDeclaration('b: 2')
        r.variables = d2
        assert r == d2.parentRule

    def test_reprANDstr(self):
        "CSSVariablesDeclaration.__repr__(), .__str__()"
        s = cssutils.css.CSSVariablesDeclaration(cssText='a:1;b:2')

        assert "2" in str(s)  # length

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
