"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""

import types
import xml.dom

import pytest

import cssutils

from . import basetest


@pytest.fixture
def set_r_property_value(request):
    request.instance.r = cssutils.css.PropertyValue()


@pytest.mark.usefixtures('set_r_property_value')
class TestPropertyValue(basetest.BaseTestCase):
    def test_init(self):
        "PropertyValue.__init__() .item() .length"
        pv = cssutils.css.PropertyValue()
        assert '' == pv.cssText
        assert 0 == pv.length
        assert '' == pv.value

        cssText = '0, 0/0 1px var(x) url(x)'
        items = ['0', '0', '0', '1px', 'var(x)', 'url(x)']
        pv = cssutils.css.PropertyValue(cssText)
        assert cssText == pv.cssText
        assert 6 == len(pv)
        assert 6 == pv.length

        # __iter__
        for i, x in enumerate(pv):
            assert x.cssText == items[i]

        # cssText
        for i, item in enumerate(items):
            assert item == pv[i].cssText
            assert item == pv.item(i).cssText

    def test_cssText(self):
        "PropertyValue.cssText"
        tests = {
            '0': (None, 1, None),
            '0 0': (None, 2, None),
            '0, 0': (None, 2, None),
            '0,0': ('0, 0', 2, None),
            '0  ,   0': ('0, 0', 2, None),
            '0/0': (None, 2, None),
            '/**/ 0 /**/': (None, 1, '0'),
            '0 /**/ 0 /**/ 0': (None, 3, '0 0 0'),
            '0, /**/ 0, /**/ 0': (None, 3, '0, 0, 0'),
            '0//**/ 0//**/ 0': (None, 3, '0/0/0'),
            '/**/ red': (None, 1, 'red'),
            '/**/red': ('/**/ red', 1, 'red'),
            'red /**/': (None, 1, 'red'),
            'red/**/': ('red /**/', 1, 'red'),
            'a()1,-1,+1,1%,-1%,1px,-1px,"a",a,url(a),#aabb44': (
                'a() 1, -1, +1, 1%, -1%, 1px, -1px, "a", a, url(a), #ab4',
                12,
                'a() 1, -1, +1, 1%, -1%, 1px, -1px, "a", a, url(a), #ab4',
            ),
            # calc values
            'calc(1)': (None, 1, 'calc(1)'),
            'calc( 1)': ('calc(1)', 1, 'calc(1)'),
            'calc(1 )': ('calc(1)', 1, 'calc(1)'),
            'calc(1px)': (None, 1, 'calc(1px)'),
            'calc(1p-x-)': (None, 1, 'calc(1p-x-)'),
            'calc(1%)': (None, 1, 'calc(1%)'),
            'calc(-1)': (None, 1, 'calc(-1)'),
            'calc(+1)': (None, 1, 'calc(+1)'),
            'calc(1  +   1px)': ('calc(1 + 1px)', 1, 'calc(1 + 1px)'),
            'calc(1 - 1px)': (None, 1, 'calc(1 - 1px)'),
            'calc(1*1px)': ('calc(1 * 1px)', 1, 'calc(1 * 1px)'),
            'calc(1  /  1px)': ('calc(1 / 1px)', 1, 'calc(1 / 1px)'),
            'calc( 1*1px)': ('calc(1 * 1px)', 1, 'calc(1 * 1px)'),
            'calc( 1  /  1px)': ('calc(1 / 1px)', 1, 'calc(1 / 1px)'),
            'calc(1*1px )': ('calc(1 * 1px)', 1, 'calc(1 * 1px)'),
            'calc(1  /  1px )': ('calc(1 / 1px)', 1, 'calc(1 / 1px)'),
            'calc( 1*1px )': ('calc(1 * 1px)', 1, 'calc(1 * 1px)'),
            'calc( 1  /  1px )': ('calc(1 / 1px)', 1, 'calc(1 / 1px)'),
            'calc(calc(1px + 5px) * 4)': (
                'calc(calc(1px + 5px) * 4)',
                1,
                'calc(calc(1px + 5px) * 4)',
            ),
            'calc( calc(1px + 5px)*4 )': (
                'calc(calc(1px + 5px) * 4)',
                1,
                'calc(calc(1px + 5px) * 4)',
            ),
            'calc(var(X))': (None, 1, None),
            'calc(2 * var(X))': (None, 1, None),
            'calc(2px + var(X))': (None, 1, None),
            # issue #24
            'rgb(0, 10, 255)': (None, 1, 'rgb(0, 10, 255)'),
            'hsl(10, 10%, 25%)': (None, 1, 'hsl(10, 10%, 25%)'),
            'rgba(0, 10, 255, 0.5)': (None, 1, 'rgba(0, 10, 255, 0.5)'),
            'hsla(10, 10%, 25%, 0.5)': (None, 1, 'hsla(10, 10%, 25%, 0.5)'),
            # issue #27
            'matrix(0.000092, 0.2500010, -0.250000, 0.000092, 0, 0)': (
                'matrix(0.000092, 0.250001, -0.25, 0.000092, 0, 0)',
                1,
                'matrix(0.000092, 0.250001, -0.25, 0.000092, 0, 0)',
            ),
        }
        for cssText, (c, len, v) in list(tests.items()):
            if c is None:
                c = cssText
            if v is None:
                v = c

            pv = cssutils.css.PropertyValue(cssText)
            assert c == pv.cssText
            assert len == pv.length
            assert v == pv.value

        tests = {
            '0 0px -0px +0px': ('0 0 0 0', 4),
            '1 2 3 4': (None, 4),
            '-1 -2 -3 -4': (None, 4),
            '-1 2': (None, 2),
            '-1px red "x"': (None, 3),
            'a, b c': (None, 3),
            '1px1 2% 3': ('1px1 2% 3', 3),
            'f(+1pX, -2, 5%) 1': ('f(+1px, -2, 5%) 1', 2),
            '0 f()0': ('0 f() 0', 3),
            'f()0': ('f() 0', 2),
            'f()1%': ('f() 1%', 2),
            'f()1px': ('f() 1px', 2),
            'f()"str"': ('f() "str"', 2),
            'f()ident': ('f() ident', 2),
            'f()#123': ('f() #123', 2),
            'f()url()': ('f() url()', 2),
            'f()f()': ('f() f()', 2),
            'url(x.gif)0 0': ('url(x.gif) 0 0', 3),
            'url(x.gif)no-repeat': ('url(x.gif) no-repeat', 2),
        }
        for cssText, (c, len) in list(tests.items()):
            if c is None:
                c = cssText
            pv = cssutils.css.PropertyValue(cssText)
            assert c == pv.cssText
            assert len == pv.length

        tests = {
            # hash and rgb/a
            '#112234': '#112234',
            '#112233': '#123',
            'rgb(1,2,3)': 'rgb(1, 2, 3)',
            'rgb(  1  ,  2  ,  3  )': 'rgb(1, 2, 3)',
            'rgba(1,2,3,4)': 'rgba(1, 2, 3, 4)',
            'rgba(  1  ,  2  ,  3  ,  4 )': 'rgba(1, 2, 3, 4)',
            'rgb(-1,+2,0)': 'rgb(-1, +2, 0)',
            'rgba(-1,+2,0, 0)': 'rgba(-1, +2, 0, 0)',
            # FUNCTION
            'f(1,2)': 'f(1, 2)',
            'f(  1  ,  2  )': 'f(1, 2)',
            'f(-1,+2)': 'f(-1, +2)',
            'f(  -1  ,  +2  )': 'f(-1, +2)',
            'fun(  -1  ,  +2  )': 'fun(-1, +2)',
            'local( x )': 'local(x)',
            'test(1px, #111, y, 1, 1%, "1", y(), var(x))': 'test(1px, #111, y, 1, 1%, "1", y(), var(x))',
            'test(-1px, #111, y, -1, -1%, "1", -y())': 'test(-1px, #111, y, -1, -1%, "1", -y())',
            'url(y)  format( "x" ,  "y" )': 'url(y) format("x", "y")',
            'f(1 2,3 4)': 'f(1 2, 3 4)',
            # IE expression
            r'Expression()': 'Expression()',
            r'expression(-1 < +2)': 'expression(-1<+2)',
            r'expression(document.width == "1")': 'expression(document.width=="1")',
            'alpha(opacity=80)': 'alpha(opacity=80)',
            'alpha( opacity = 80 , x=2  )': 'alpha(opacity=80, x=2)',
            'expression(eval(document.documentElement.scrollTop))': 'expression(eval(document.documentElement.scrollTop))',
            # TODO
            #            u'expression((function(ele){ele.style.behavior="none";})(this))':
            #                u'expression((function(ele){ele.style.behavior="none";})(this))',
            # unicode-range
            'u+f': 'u+f',
            'U+ABCdef': 'u+abcdef',
            # url
            'url(a)': 'url(a)',
            'uRl(a)': 'url(a)',
            'u\\rl(a)': 'url(a)',
            'url("a")': 'url(a)',
            'url(  "a"  )': 'url(a)',
            'url(";")': 'url(";")',
            'url(",")': 'url(",")',
            'url(")")': 'url(")")',
            '''url("'")''': '''url("'")''',
            '''url('"')''': '''url("\\"")''',
            # operator
            '1': '1',
            '1 2': '1 2',
            '1   2': '1 2',
            '1,2': '1, 2',
            '1,  2': '1, 2',
            '1  ,2': '1, 2',
            '1  ,  2': '1, 2',
            '1/2': '1/2',
            '1/  2': '1/2',
            '1  /2': '1/2',
            '1  /  2': '1/2',
            # comment
            '1/**/2': '1 /**/ 2',
            '1 /**/2': '1 /**/ 2',
            '1/**/ 2': '1 /**/ 2',
            '1 /**/ 2': '1 /**/ 2',
            '1  /*a*/  /*b*/  2': '1 /*a*/ /*b*/ 2',
            # , before
            '1,/**/2': '1, /**/ 2',
            '1 ,/**/2': '1, /**/ 2',
            '1, /**/2': '1, /**/ 2',
            '1 , /**/2': '1, /**/ 2',
            # , after
            '1/**/,2': '1 /**/, 2',
            '1/**/ ,2': '1 /**/, 2',
            '1/**/, 2': '1 /**/, 2',
            '1/**/ , 2': '1 /**/, 2',
            # all
            '1/*a*/  ,/*b*/  2': '1 /*a*/, /*b*/ 2',
            '1  /*a*/,  /*b*/2': '1 /*a*/, /*b*/ 2',
            '1  /*a*/  ,  /*b*/  2': '1 /*a*/, /*b*/ 2',
            # list
            'a b1,b2 b2,b3,b4': 'a b1, b2 b2, b3, b4',
            'a b1  ,   b2   b2  ,  b3  ,   b4': 'a b1, b2 b2, b3, b4',
            'u+1  ,   u+2-5': 'u+1, u+2-5',
            'local( x ),  url(y)  format( "x" ,  "y" )': 'local(x), url(y) format("x", "y")',
            # FUNCTION
            'attr( href )': 'attr(href)',
            # PrinceXML extende FUNC syntax with nested FUNC
            'target-counter(attr(href),page)': 'target-counter(attr(href), page)',
        }
        self.do_equal_r(tests)

        tests = [
            'a+',
            '-',
            '+',
            '-%',
            '+a',
            '--1px',
            '++1px',
            '#',
            '#00',
            '#12x',
            '#xyz',
            '#0000',
            '#00000',
            '#0000000',
            '-#0',
            # operator
            ',',
            '1,,2',
            '1,/**/,2',
            '1  ,  /**/  ,  2',
            '1,',
            '1, ',
            '1 ,',
            '1 , ',
            '1  ,  ',
            '1//2',
            # URL
            'url(x))',
            # string
            '"',
            "'",
            # function
            'f(-)',
            'f(x))',
            # calc
            'calc(',
            'calc(1',
            'calc(1 + 1',
            'calc(1+1)',
            'calc(1-1)',
            'calc(1 +1)',
            'calc(1+ 1)',
            'calc(1 -1)',
            'calc(1- 1)',
            'calc(+)',
            'calc(+ 1)',
            'calc(-)',
            'calc(- 1)',
            'calc(*)',
            'calc(*1)',
            'calc(* 2)',
            'calc(/)',
            'calc(/1)',
            'calc(/ 2)',
            'calc(1+)',
            'calc(1 +)',
            'calc(1 + )',
            'calc(2px -)',
            'calc(3px*)',
            'calc(3px *)',
            'calc(3px * )',
            'calc(4em/)',
            'calc(4em /)',
            'calc(4em / )',
            'calc(1 + + 1)',
            'calc(1 ++ 1)',
        ]
        self.do_raise_r_list(tests, xml.dom.SyntaxErr)

    def test_list(self):
        "PropertyValue[index]"
        # issue #41
        css = """div.one {color: rgb(255, 0, 0);}   """
        sheet = cssutils.parseString(css)
        pv = sheet.cssRules[0].style.getProperty('color').propertyValue
        assert pv.value == 'rgb(255, 0, 0)'
        assert pv[0].value == 'rgb(255, 0, 0)'

        # issue #42
        sheet = cssutils.parseString('body { font-family: "A", b, serif }')
        pv = sheet.cssRules[0].style.getProperty('font-family').propertyValue
        assert 3 == pv.length
        assert pv[0].value == 'A'
        assert pv[1].value == 'b'
        assert pv[2].value == 'serif'

    def test_comments(self):
        "PropertyValue with comment"
        # issue #45
        for t in (
            'green',
            'green /* comment */',
            '/* comment */green',
            '/* comment */green/* comment */',
            '/* comment */  green  /* comment */',
            '/* comment *//**/  green  /* comment *//**/',
        ):
            sheet = cssutils.parseString('body {color: %s; }' % t)
            p = sheet.cssRules[0].style.getProperties()[0]
            assert p.valid
        for t in (
            'gree',
            'gree /* comment */',
            '/* comment */gree',
            '/* comment */gree/* comment */',
            '/* comment */  gree  /* comment */',
            '/* comment *//**/  gree  /* comment *//**/',
        ):
            sheet = cssutils.parseString('body {color: %s; }' % t)
            p = sheet.cssRules[0].style.getProperties()[0]
            assert not p.valid

    def test_incomplete(self):
        "PropertyValue (incomplete)"
        tests = {'url("a': 'url(a)', 'url(a': 'url(a)'}
        for v, exp in list(tests.items()):
            s = cssutils.parseString('a { background: %s' % v)
            v = s.cssRules[0].style.background
            assert v == exp

    def test_readonly(self):
        "PropertyValue._readonly"
        v = cssutils.css.PropertyValue(cssText='inherit')
        assert False is v._readonly

        v = cssutils.css.PropertyValue(cssText='inherit', readonly=True)
        assert True is v._readonly
        assert 'inherit', v.cssText
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            v._setCssText('x')
        assert 'inherit', v.cssText

    def test_reprANDstr(self):
        "PropertyValue.__repr__(), .__str__()"
        cssText = 'inherit'

        s = cssutils.css.PropertyValue(cssText=cssText)

        assert cssText in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert cssText == s2.cssText


class TestValue:
    def test_init(self):
        "Value.__init__()"
        v = cssutils.css.Value()
        assert '' == v.cssText
        assert '' == v.value
        assert None is v.type

    def test_cssText(self):
        "Value.cssText"
        # HASH IDENT STRING UNICODE-RANGE
        tests = {
            '#123': ('#123', '#123', 'HASH'),
            '#123456': ('#123456', '#123456', 'HASH'),
            '#112233': ('#123', '#112233', 'HASH'),
            '  #112233  ': ('#123', '#112233', 'HASH'),
            'red': ('red', 'red', 'IDENT'),
            '  red  ': ('red', 'red', 'IDENT'),
            'red  ': ('red', 'red', 'IDENT'),
            '  red': ('red', 'red', 'IDENT'),
            'red-': ('red-', 'red-', 'IDENT'),
            '-red': ('-red', '-red', 'IDENT'),
            '"red"': ('"red"', 'red', 'STRING'),
            "'red'": ('"red"', 'red', 'STRING'),
            '  "red"  ': ('"red"', 'red', 'STRING'),
            r'"red\""': (r'"red\""', r'red"', 'STRING'),
            r"'x\"'": (r'"x\\""', r'x\"', 'STRING'),  # ???
            '''"x\
y"''': (
                '"xy"',
                'xy',
                'STRING',
            ),
        }
        for p, (r, n, t) in list(tests.items()):
            v = cssutils.css.Value(p)
            assert r == v.cssText
            assert t == v.type
            assert n == v.value


class TestColorValue(basetest.BaseTestCase):
    def test_init(self):
        "ColorValue.__init__()"
        v = cssutils.css.ColorValue()
        assert v.COLOR_VALUE == v.type
        assert '' == v.cssText
        assert '' == v.value
        assert 'transparent' == v.name
        assert v.colorType is None

    def test_cssText(self):
        "ColorValue.cssText"
        tests = {
            # HASH
            '#123': ('#123',),
            '#112233': ('#123',),
            # rgb
            'rgb(1,2,3)': ('rgb(1, 2, 3)',),
            'rgb(1%,2%,3%)': ('rgb(1%, 2%, 3%)',),
            'rgb(-1,-1,-1)': ('rgb(-1, -1, -1)',),
            'rgb(-1%,-2%,-3%)': ('rgb(-1%, -2%, -3%)',),
            # rgba
            'rgba(1,2,3, 0)': ('rgba(1, 2, 3, 0)',),
            # hsl
            'hsl(1,2%,3%)': ('hsl(1, 2%, 3%)',),
            'hsla(1,2%,3%, 1.0)': ('hsla(1, 2%, 3%, 1)',),
        }
        for p, (r,) in list(tests.items()):
            v = cssutils.css.ColorValue(p)
            assert v.COLOR_VALUE == v.type
            assert r == v.cssText
            assert r == v.value

            v = cssutils.css.ColorValue()
            v.cssText = p
            assert v.COLOR_VALUE == v.type
            assert r == v.cssText
            assert r == v.value

        tests = {
            '1': xml.dom.SyntaxErr,
            'a': xml.dom.SyntaxErr,
            '#12': xml.dom.SyntaxErr,
            '#1234': xml.dom.SyntaxErr,
            '#1234567': xml.dom.SyntaxErr,
            '#12345678': xml.dom.SyntaxErr,
            'rgb(1,1%,1%)': xml.dom.SyntaxErr,
            'rgb(1%,1,1)': xml.dom.SyntaxErr,
            'rgb(-1,-1%,-1%)': xml.dom.SyntaxErr,
            'rgb(-1%,-1,-1)': xml.dom.SyntaxErr,
            'rgb(1,1,1, 0)': xml.dom.SyntaxErr,
            'rgb(1%,1%,1%, 0)': xml.dom.SyntaxErr,
            'rgba(1,1,1)': xml.dom.SyntaxErr,
            'rgba(1%,1%,1%)': xml.dom.SyntaxErr,
            'rgba(1,1,1, 0%)': xml.dom.SyntaxErr,
            'rgba(1%,1%,1%, 0%)': xml.dom.SyntaxErr,
            'hsl(1,2%,3%, 1)': xml.dom.SyntaxErr,
            'hsla(1,2%,3%)': xml.dom.SyntaxErr,
            'hsl(1,2,3)': xml.dom.SyntaxErr,
            'hsl(1%,2,3)': xml.dom.SyntaxErr,
            'hsl(1%,2,3%)': xml.dom.SyntaxErr,
            'hsl(1%,2%,3)': xml.dom.SyntaxErr,
            'hsla(1,2%,3%, 0%)': xml.dom.SyntaxErr,
            'hsla(1,2,3, 0.0)': xml.dom.SyntaxErr,
            'hsla(1%,2,3, 0.0)': xml.dom.SyntaxErr,
            'hsla(1%,2,3%, 0.0)': xml.dom.SyntaxErr,
            'hsla(1%,2%,3, 0.0)': xml.dom.SyntaxErr,
        }
        self.r = cssutils.css.ColorValue()
        self.do_raise_r(tests)

    def test_rgb(self):
        "ColorValue.red .green .blue"
        tests = {
            ('#0A0AD2', 'rgb(10, 10, 210)'): (10, 10, 210, 1.0),
            # TODO: Fix rounding?
            ('hsl(240, 91%, 43%)',): (10, 10, 209, 1.0),
            ('#ff8800', '#f80', 'rgb(255, 136, 0)', 'rgba(255, 136, 0, 1.0)'): (
                255,
                136,
                0,
                1.0,
            ),
            (
                'red',
                '#ff0000',
                '#f00',
                'hsl(0, 100%, 50%)',
                'hsla(0, 100%, 50%, 1.0)',
            ): (255, 0, 0, 1.0),
            ('lime', '#00ff00', '#0f0', 'hsl(120, 100%, 50%)'): (0, 255, 0, 1.0),
            ('rgba(255, 127, 0, .1)', 'rgba(100%, 50%, 0%, .1)'): (255, 127, 0, 0.1),
            ('transparent', 'rgba(0, 0, 0, 0)'): (0, 0, 0, 0),
            ('aqua',): (0, 255, 255, 1.0),
        }
        for colors, rgba in list(tests.items()):
            for color in colors:
                c = cssutils.css.ColorValue(color)
                assert c.red == rgba[0]
                assert c.green == rgba[1]
                assert c.blue == rgba[2]
                assert c.alpha == rgba[3]


class TestURIValue(basetest.BaseTestCase):
    def test_init(self):
        "URIValue.__init__()"
        v = cssutils.css.URIValue()
        assert 'url()' == v.cssText
        assert '' == v.value
        assert '' == v.uri
        assert v.URI is v.type

        v.uri = '1'
        assert '1' == v.value
        assert '1' == v.uri
        assert 'url(1)' == v.cssText

        v.value = '2'
        assert '2' == v.value
        assert '2' == v.uri
        assert 'url(2)' == v.cssText

    def test_absoluteUri(self):
        "URIValue.absoluteUri"
        s = cssutils.parseString(
            'a { background-image: url(x.gif)}', href="/path/to/x.css"
        )
        v = s.cssRules[0].style.getProperty('background-image').propertyValue[0]
        assert 'x.gif' == v.uri
        assert '/path/to/x.gif' == v.absoluteUri

        v = cssutils.css.URIValue('url(x.gif)')
        assert 'x.gif' == v.uri
        assert 'x.gif' == v.absoluteUri

    def test_cssText(self):
        "URIValue.cssText"
        tests = {
            'url()': ('url()', '', 'URI'),
            # comments are part of the url!
            'url(/**/)': ('url(/**/)', '/**/', 'URI'),
            'url(/**/1)': ('url(/**/1)', '/**/1', 'URI'),
            'url(1/**/)': ('url(1/**/)', '1/**/', 'URI'),
            'url(/**/1/**/)': ('url(/**/1/**/)', '/**/1/**/', 'URI'),
            'url(some.gif)': ('url(some.gif)', 'some.gif', 'URI'),
            '  url(some.gif)  ': ('url(some.gif)', 'some.gif', 'URI'),
            'url(   some.gif  )': ('url(some.gif)', 'some.gif', 'URI'),
        }
        for p, (r, n, t) in list(tests.items()):
            v = cssutils.css.URIValue(p)
            assert r == v.cssText
            assert t == v.type
            assert n == v.value
            assert n == v.uri

            v = cssutils.css.URIValue()
            v.cssText = p
            assert r == v.cssText
            assert t == v.type
            assert n == v.value
            assert n == v.uri

        tests = {
            'a()': xml.dom.SyntaxErr,
            '1': xml.dom.SyntaxErr,
            'url(': xml.dom.SyntaxErr,
            'url("': xml.dom.SyntaxErr,
            'url(\'': xml.dom.SyntaxErr,
        }
        self.r = cssutils.css.URIValue()
        self.do_raise_r(tests)


class TestDimensionValue:
    def test_init(self):
        "DimensionValue.__init__()"
        v = cssutils.css.DimensionValue()
        assert '' == v.cssText
        assert '' == v.value
        assert None is v.type
        assert None is v.dimension

    def test_cssText(self):
        "DimensionValue.cssText"
        # NUMBER DIMENSION PERCENTAGE
        tests = {
            '0': ('0', 0, None, 'NUMBER'),
            '00': ('0', 0, None, 'NUMBER'),
            '.0': ('0', 0, None, 'NUMBER'),
            '0.0': ('0', 0, None, 'NUMBER'),
            '+0': ('0', 0, None, 'NUMBER'),
            '+00': ('0', 0, None, 'NUMBER'),
            '+.0': ('0', 0, None, 'NUMBER'),
            '+0.0': ('0', 0, None, 'NUMBER'),
            '-0': ('0', 0, None, 'NUMBER'),
            '-00': ('0', 0, None, 'NUMBER'),
            '-.0': ('0', 0, None, 'NUMBER'),
            '-0.0': ('0', 0, None, 'NUMBER'),
            '1': ('1', 1, None, 'NUMBER'),
            '1.0': ('1', 1.0, None, 'NUMBER'),
            '1.1': ('1.1', 1.1, None, 'NUMBER'),
            '+1': ('+1', 1, None, 'NUMBER'),
            '+1.0': ('+1', 1.0, None, 'NUMBER'),
            '+1.1': ('+1.1', 1.1, None, 'NUMBER'),
            '-1': ('-1', -1, None, 'NUMBER'),
            '-1.0': ('-1', -1, None, 'NUMBER'),
            '-1.1': ('-1.1', -1.1, None, 'NUMBER'),
            '0px': ('0', 0, 'px', 'DIMENSION'),
            '1px': ('1px', 1, 'px', 'DIMENSION'),
            '1.0px': ('1px', 1.0, 'px', 'DIMENSION'),
            '1.1px': ('1.1px', 1.1, 'px', 'DIMENSION'),
            '-1px': ('-1px', -1, 'px', 'DIMENSION'),
            '-1.1px': ('-1.1px', -1.1, 'px', 'DIMENSION'),
            '+1px': ('+1px', 1, 'px', 'DIMENSION'),
            '1px1': ('1px1', 1, 'px1', 'DIMENSION'),
            '0%': ('0%', 0, '%', 'PERCENTAGE'),
            '1%': ('1%', 1, '%', 'PERCENTAGE'),
            '1.1%': ('1.1%', 1.1, '%', 'PERCENTAGE'),
            '-1%': ('-1%', -1, '%', 'PERCENTAGE'),
            '-1.1%': ('-1.1%', -1.1, '%', 'PERCENTAGE'),
            '+1%': ('+1%', 1, '%', 'PERCENTAGE'),
        }
        for p, (r, n, d, t) in list(tests.items()):
            v = cssutils.css.DimensionValue(p)
            assert r == v.cssText
            assert t == v.type
            assert n == v.value
            assert d == v.dimension


class TestCSSFunction:
    def test_init(self):
        "CSSFunction.__init__()"
        v = cssutils.css.CSSFunction()
        assert '' == v.cssText
        assert 'FUNCTION' == v.type
        assert v.value == ''

    def test_cssText(self):
        "CSSFunction.cssText"
        tests = {
            'x(x)': ('x(x)', None),
            'X(  X  )': ('x(X)', None),
            'x(1,2)': ('x(1, 2)', None),
            'x(1/**/)': ('x(1 /**/)', 'x(1)'),
            'x(/**/1)': ('x(/**/ 1)', 'x(1)'),
            'x(/**/1/**/)': ('x(/**/ 1 /**/)', 'x(1)'),
            'x(/**/1,x/**/)': ('x(/**/ 1, x /**/)', 'x(1, x)'),
        }
        for f, (cssText, value) in list(tests.items()):
            if value is None:
                value = cssText
            v = cssutils.css.CSSFunction(f)
            assert cssText == v.cssText
            assert 'FUNCTION' == v.type
            assert value == v.value


class TestCSSVariable:
    def test_init(self):
        "CSSVariable.__init__()"
        v = cssutils.css.CSSVariable()
        assert '' == v.cssText
        assert 'VARIABLE' == v.type
        assert None is v.name
        assert None is v.value

    def test_cssText(self):
        "CSSVariable.cssText"
        tests = {
            'var(x)': ('var(x)', 'x', None),
            'VAR(  X  )': ('var(X)', 'X', None),
            'var(c1,rgb(14,14,14))': (
                'var(c1, rgb(14, 14, 14))',
                'c1',
                'rgb(14, 14, 14)',
            ),
            'var( L, 1px )': ('var(L, 1px)', 'L', '1px'),
            'var(L,1)': ('var(L, 1)', 'L', '1'),
            'var(T, calc( 2 * 1px ))': ('var(T, calc(2 * 1px))', 'T', 'calc(2 * 1px)'),
            'var(U, url( example.png ) )': (
                'var(U, url(example.png))',
                'U',
                'url(example.png)',
            ),
            'var(C, #f00 )': ('var(C, #f00)', 'C', '#fff'),
        }
        for var, (cssText, name, _fallback) in list(tests.items()):
            v = cssutils.css.CSSVariable(var)
            assert cssText == v.cssText
            assert 'VARIABLE' == v.type
            assert name == v.name
            # not resolved so it is None
            assert v.value is None

    @pytest.mark.xfail(reason="not implemented")
    def test_cssValueType(self):
        "CSSValue.cssValueType .cssValueTypeString"
        tests = [
            (['inherit', 'INhe\\rit'], 'CSS_INHERIT', cssutils.css.CSSValue),
            (
                [
                    '1',
                    '1%',
                    '1em',
                    '1ex',
                    '1px',
                    '1cm',
                    '1mm',
                    '1in',
                    '1pt',
                    '1pc',
                    '1deg',
                    '1rad',
                    '1grad',
                    '1ms',
                    '1s',
                    '1hz',
                    '1khz',
                    '1other',
                    '"string"',
                    "'string'",
                    'url(x)',
                    'red',
                    'attr(a)',
                    'counter(x)',
                    'rect(1px, 2px, 3px, 4px)',
                    'rgb(0, 0, 0)',
                    '#000',
                    '#123456',
                    'rgba(0, 0, 0, 0)',
                    'hsl(0, 0, 0)',
                    'hsla(0, 0, 0, 0)',
                ],
                'CSS_PRIMITIVE_VALUE',
                cssutils.css.CSSPrimitiveValue,
            ),
            (
                ['1px 1px', 'red blue green x'],
                'CSS_VALUE_LIST',
                cssutils.css.CSSValueList,
            ),
            # what is a custom value?
            # ([], 'CSS_CUSTOM', cssutils.css.CSSValue)
        ]
        for values, name, cls in tests:
            for value in values:
                v = cssutils.css.CSSValue(cssText=value)
                if value == "'string'":
                    # will be changed to " always
                    value = '"string"'
                assert value == v.cssText
                assert name == v.cssValueTypeString
                assert getattr(v, name) == v.cssValueType
                assert cls == type(v)


@pytest.mark.xfail(reason="not implemented")
class TestCSSPrimitiveValue:
    def test_init(self):
        "CSSPrimitiveValue.__init__()"
        v = cssutils.css.CSSPrimitiveValue('1')
        assert '1' == v.cssText

        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert "CSS_PRIMITIVE_VALUE" == v.cssValueTypeString

        assert v.CSS_NUMBER == v.primitiveType
        assert "CSS_NUMBER" == v.primitiveTypeString

        # DUMMY to be able to test empty constructor call
        # self.assertRaises(xml.dom.SyntaxErr, v.__init__, None)

        with pytest.raises(xml.dom.InvalidAccessErr):
            v.getCounterValue()
        with pytest.raises(xml.dom.InvalidAccessErr):
            v.getRGBColorValue()
        with pytest.raises(xml.dom.InvalidAccessErr):
            v.getRectValue()
        with pytest.raises(xml.dom.InvalidAccessErr):
            v.getStringValue()

    def test_CSS_UNKNOWN(self):
        "CSSPrimitiveValue.CSS_UNKNOWN"
        v = cssutils.css.CSSPrimitiveValue('expression(false)')
        assert v.CSS_UNKNOWN == v.primitiveType
        assert 'CSS_UNKNOWN' == v.primitiveTypeString

    def test_CSS_NUMBER_AND_OTHER_DIMENSIONS(self):
        "CSSPrimitiveValue.CSS_NUMBER .. CSS_DIMENSION"
        defs = [
            ('', 'CSS_NUMBER'),
            ('%', 'CSS_PERCENTAGE'),
            ('em', 'CSS_EMS'),
            ('ex', 'CSS_EXS'),
            ('px', 'CSS_PX'),
            ('cm', 'CSS_CM'),
            ('mm', 'CSS_MM'),
            ('in', 'CSS_IN'),
            ('pt', 'CSS_PT'),
            ('pc', 'CSS_PC'),
            ('deg', 'CSS_DEG'),
            ('rad', 'CSS_RAD'),
            ('grad', 'CSS_GRAD'),
            ('ms', 'CSS_MS'),
            ('s', 'CSS_S'),
            ('hz', 'CSS_HZ'),
            ('khz', 'CSS_KHZ'),
            ('other_dimension', 'CSS_DIMENSION'),
        ]
        for dim, name in defs:
            for n in (0, 1, 1.1, -1, -1.1, -0):
                v = cssutils.css.CSSPrimitiveValue('%i%s' % (n, dim))
                assert name == v.primitiveTypeString
                assert getattr(v, name) == v.primitiveType

    def test_CSS_STRING_AND_OTHER(self):
        "CSSPrimitiveValue.CSS_STRING .. CSS_RGBCOLOR"
        defs = [
            (
                (
                    '""',
                    "''",
                    '"some thing"',
                    "' A\\ND '",
                    # comma separated lists are STRINGS FOR NOW!
                    'a, b',
                    '"a", "b"',
                ),
                'CSS_STRING',
            ),
            (('url(a)', 'url("a b")', "url(' ')"), 'CSS_URI'),
            (('some', 'or_anth-er'), 'CSS_IDENT'),
            (('attr(a)', 'attr(b)'), 'CSS_ATTR'),
            (('counter(1)', 'counter(2)'), 'CSS_COUNTER'),
            (('rect(1,2,3,4)',), 'CSS_RECT'),
            (('rgb(1,2,3)', 'rgb(10%, 20%, 30%)', '#123', '#123456'), 'CSS_RGBCOLOR'),
            (
                (
                    'rgba(1,2,3,4)',
                    'rgba(10%, 20%, 30%, 40%)',
                ),
                'CSS_RGBACOLOR',
            ),
            (('U+0', 'u+ffffff', 'u+000000-f', 'u+0-f, U+ee-ff'), 'CSS_UNICODE_RANGE'),
        ]

        for examples, name in defs:
            for x in examples:
                v = cssutils.css.CSSPrimitiveValue(x)
                assert getattr(v, name) == v.primitiveType
                assert name == v.primitiveTypeString

    def test_getFloat(self):
        "CSSPrimitiveValue.getFloatValue()"
        # NOT TESTED are float values as it seems difficult to
        # compare these. Maybe use decimal.Decimal?

        v = cssutils.css.CSSPrimitiveValue('1px')
        tests = {
            '0': (v.CSS_NUMBER, 0),
            '-1.1': (v.CSS_NUMBER, -1.1),
            '1%': (v.CSS_PERCENTAGE, 1),
            '-1%': (v.CSS_PERCENTAGE, -1),
            '1em': (v.CSS_EMS, 1),
            '-1.1em': (v.CSS_EMS, -1.1),
            '1ex': (v.CSS_EXS, 1),
            '1px': (v.CSS_PX, 1),
            '1cm': (v.CSS_CM, 1),
            # '1cm': (v.CSS_MM, 10),
            '254cm': (v.CSS_IN, 100),
            '1mm': (v.CSS_MM, 1),
            '10mm': (v.CSS_CM, 1),
            '254mm': (v.CSS_IN, 10),
            '1in': (v.CSS_IN, 1),
            '100in': (v.CSS_CM, 254),  # ROUNDED!!!
            '10in': (v.CSS_MM, 254),  # ROUNDED!!!
            '1pt': (v.CSS_PT, 1),
            '1pc': (v.CSS_PC, 1),
            '1deg': (v.CSS_DEG, 1),
            '1rad': (v.CSS_RAD, 1),
            '1grad': (v.CSS_GRAD, 1),
            '1ms': (v.CSS_MS, 1),
            '1000ms': (v.CSS_S, 1),
            '1s': (v.CSS_S, 1),
            # '1s': (v.CSS_MS, 1000),
            '1hz': (v.CSS_HZ, 1),
            '1000hz': (v.CSS_KHZ, 1),
            '1khz': (v.CSS_KHZ, 1),
            # '1khz': (v.CSS_HZ, 1000),
            '1DIMENSION': (v.CSS_DIMENSION, 1),
        }
        for cssText in tests:
            v.cssText = cssText
            unitType, exp = tests[cssText]
            val = v.getFloatValue(unitType)
            if unitType in (v.CSS_IN, v.CSS_CM):
                val = round(val)
            assert val == exp

    def test_setFloat(self):
        "CSSPrimitiveValue.setFloatValue()"
        V = cssutils.css.CSSPrimitiveValue

        tests = {
            # unitType, value
            (V.CSS_NUMBER, 1): [
                # unitType, setvalue,
                #    getvalue or expected exception, msg or cssText
                (V.CSS_NUMBER, 0, 0, '0'),
                (V.CSS_NUMBER, 0.1, 0.1, '0.1'),
                (V.CSS_NUMBER, -0, 0, '0'),
                (V.CSS_NUMBER, 2, 2, '2'),
                (V.CSS_NUMBER, 2.0, 2, '2'),
                (V.CSS_NUMBER, 2.1, 2.1, '2.1'),
                (V.CSS_NUMBER, -2.1, -2.1, '-2.1'),
                # setting with string does work
                (V.CSS_NUMBER, '1', 1, '1'),
                (V.CSS_NUMBER, '1.1', 1.1, '1.1'),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DEG, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_RAD, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_GRAD, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_S, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_MS, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_KHZ, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_HZ, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DIMENSION, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_MM, 2, xml.dom.InvalidAccessErr, None),
                (
                    V.CSS_NUMBER,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: floatValue 'x' is not a float",
                ),
                (
                    V.CSS_NUMBER,
                    '1x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: floatValue '1x' is not a float",
                ),
                (
                    V.CSS_STRING,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_STRING' is not a float type",
                ),
                (
                    V.CSS_URI,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_URI' is not a float type",
                ),
                (
                    V.CSS_ATTR,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_ATTR' is not a float type",
                ),
                (
                    V.CSS_IDENT,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_IDENT' is not a float type",
                ),
                (
                    V.CSS_RGBCOLOR,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_RGBCOLOR' is not a float type",
                ),
                (
                    V.CSS_RGBACOLOR,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_RGBACOLOR' is not a float type",
                ),
                (
                    V.CSS_RECT,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_RECT' is not a float type",
                ),
                (
                    V.CSS_COUNTER,
                    'x',
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: unitType 'CSS_COUNTER' is not a float type",
                ),
                (
                    V.CSS_EMS,
                    1,
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_NUMBER' to 'CSS_EMS'",
                ),
                (
                    V.CSS_EXS,
                    1,
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_NUMBER' to 'CSS_EXS'",
                ),
            ],
            (V.CSS_MM, '1mm'): [
                (V.CSS_MM, 2, 2, '2mm'),
                (V.CSS_MM, 0, 0, '0mm'),
                (V.CSS_MM, 0.1, 0.1, '0.1mm'),
                (V.CSS_MM, -0, -0, '0mm'),
                (V.CSS_MM, 3.0, 3, '3mm'),
                (V.CSS_MM, 3.1, 3.1, '3.1mm'),
                (V.CSS_MM, -3.1, -3.1, '-3.1mm'),
                (V.CSS_CM, 1, 10, '10mm'),
                (V.CSS_IN, 10, 254, '254mm'),
                (V.CSS_PT, 1, 1828.8, '1828.8mm'),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_NUMBER, 2, xml.dom.InvalidAccessErr, None),
            ],
            (V.CSS_PT, '1pt'): [
                (V.CSS_PT, 2, 2, '2pt'),
                (V.CSS_PC, 12, 1, '1pt'),
                (V.CSS_NUMBER, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DEG, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None),
            ],
            (V.CSS_KHZ, '1khz'): [
                (V.CSS_HZ, 2000, 2, '2khz'),
                (V.CSS_NUMBER, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DEG, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None),
            ],
        }
        for test in tests:
            initialType, initialValue = test
            pv = cssutils.css.CSSPrimitiveValue(initialValue)
            for setType, setValue, exp, cssText in tests[test]:
                if isinstance(exp, types.TypeType):
                    if cssText:
                        self.assertRaisesMsg(
                            exp, cssText, pv.setFloatValue, setType, setValue
                        )
                    else:
                        with pytest.raises(exp):
                            pv.setFloatValue(setType, setValue)
                else:
                    pv.setFloatValue(setType, setValue)
                    assert pv._value[0] == cssText
                    if cssText == '0mm':
                        cssText = '0'
                    assert pv.cssText == cssText
                    assert pv.getFloatValue(initialType) == exp

    def test_getString(self):
        "CSSPrimitiveValue.getStringValue()"
        v = cssutils.css.CSSPrimitiveValue('1px')
        assert v.primitiveType == v.CSS_PX
        with pytest.raises(xml.dom.InvalidAccessErr):
            v.getStringValue()

        pv = cssutils.css.CSSPrimitiveValue
        tests = {
            pv.CSS_STRING: ("'red'", 'red'),
            pv.CSS_STRING: ('"red"', 'red'),
            pv.CSS_URI: ('url(http://example.com)', None),
            pv.CSS_URI: ("url('http://example.com')", "http://example.com"),
            pv.CSS_URI: ('url("http://example.com")', 'http://example.com'),
            pv.CSS_URI: ('url("http://example.com?)")', 'http://example.com?)'),
            pv.CSS_IDENT: ('red', None),
            pv.CSS_ATTR: ('attr(att-name)', 'att-name'),  # the name of the attrr
        }
        for t in tests:
            val, exp = tests[t]
            if not exp:
                exp = val

            v = cssutils.css.CSSPrimitiveValue(val)
            assert v.primitiveType == t
            assert v.getStringValue() == exp

    def test_setString(self):
        "CSSPrimitiveValue.setStringValue()"
        # CSS_STRING
        v = cssutils.css.CSSPrimitiveValue('"a"')
        assert v.CSS_STRING == v.primitiveType
        v.setStringValue(v.CSS_STRING, 'b')
        assert ('b', 'STRING') == v._value
        assert 'b' == v.getStringValue()
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_STRING' to 'CSS_URI'",
        ):
            v.setStringValue(v.CSS_URI, 'x')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_STRING' to 'CSS_IDENT'",
        ):
            v.setStringValue(v.CSS_IDENT, 'x')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_STRING' to 'CSS_ATTR'",
        ):
            v.setStringValue(v.CSS_ATTR, 'x')

        # CSS_IDENT
        v = cssutils.css.CSSPrimitiveValue('new')
        v.setStringValue(v.CSS_IDENT, 'ident')
        assert v.CSS_IDENT == v.primitiveType
        assert ('ident', 'IDENT') == v._value
        assert 'ident' == v.getStringValue()
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_IDENT' to 'CSS_URI'",
        ):
            v.setStringValue(v.CSS_URI, 'x')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_IDENT' to 'CSS_STRING'",
        ):
            v.setStringValue(v.CSS_STRING, '"x"')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_IDENT' to 'CSS_ATTR'",
        ):
            v.setStringValue(v.CSS_ATTR, 'x')

        # CSS_URI
        v = cssutils.css.CSSPrimitiveValue('url(old)')
        v.setStringValue(v.CSS_URI, '(')
        assert ('(', 'URI') == v._value
        assert '(' == v.getStringValue()

        v.setStringValue(v.CSS_URI, ')')
        assert (')', 'URI') == v._value
        assert ')' == v.getStringValue()

        v.setStringValue(v.CSS_URI, '"')
        assert '"' == v.getStringValue()
        assert ('"', 'URI') == v._value

        v.setStringValue(v.CSS_URI, "''")
        assert "''" == v.getStringValue()
        assert ("''", 'URI') == v._value

        v.setStringValue(v.CSS_URI, ',')
        assert ',' == v.getStringValue()
        assert (',', 'URI') == v._value

        v.setStringValue(v.CSS_URI, ' ')
        assert (' ', 'URI') == v._value
        assert ' ' == v.getStringValue()

        v.setStringValue(v.CSS_URI, 'a)')
        assert ('a)', 'URI') == v._value
        assert 'a)' == v.getStringValue()

        v.setStringValue(v.CSS_URI, 'a')
        assert v.CSS_URI == v.primitiveType
        assert ('a', 'URI') == v._value
        assert 'a' == v.getStringValue()

        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_URI' to 'CSS_IDENT'",
        ):
            v.setStringValue(v.CSS_IDENT, 'x')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_URI' to 'CSS_STRING'",
        ):
            v.setStringValue(v.CSS_STRING, '"x"')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_URI' to 'CSS_ATTR'",
        ):
            v.setStringValue(v.CSS_ATTR, 'x')

        # CSS_ATTR
        v = cssutils.css.CSSPrimitiveValue('attr(old)')
        v.setStringValue(v.CSS_ATTR, 'a')
        assert v.CSS_ATTR == v.primitiveType
        assert 'a' == v.getStringValue()
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_ATTR' to 'CSS_IDENT'",
        ):
            v.setStringValue(v.CSS_IDENT, 'x')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_ATTR' to 'CSS_STRING'",
        ):
            v.setStringValue(v.CSS_STRING, '"x"')
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_ATTR' to 'CSS_URI'",
        ):
            v.setStringValue(v.CSS_URI, 'x')

        # TypeError as 'x' is no valid type
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: stringType 'x' (UNKNOWN TYPE) is not a string type",
        ):
            v.setStringValue('x', 'brown')
        # IndexError as 111 is no valid type
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: stringType 111 (UNKNOWN TYPE) is not a string type",
        ):
            v.setStringValue(111, 'brown')
        # CSS_PX is no string type
        with pytest.raises(
            xml.dom.InvalidAccessErr,
            match="CSSPrimitiveValue: stringType CSS_PX is not a string type",
        ):
            v.setStringValue(v.CSS_PX, 'brown')

    def test_typeRGBColor(self):
        "RGBColor"
        v = cssutils.css.CSSPrimitiveValue('RGB(1, 5, 10)')
        assert v.CSS_RGBCOLOR == v.primitiveType
        assert 'rgb(1, 5, 10)' == v.cssText

        v = cssutils.css.CSSPrimitiveValue('rgb(1, 5, 10)')
        assert v.CSS_RGBCOLOR == v.primitiveType
        assert 'rgb(1, 5, 10)' == v.cssText

        v = cssutils.css.CSSPrimitiveValue('rgb(1%, 5%, 10%)')
        assert v.CSS_RGBCOLOR == v.primitiveType
        assert 'rgb(1%, 5%, 10%)' == v.cssText

        v = cssutils.css.CSSPrimitiveValue('  rgb(  1 ,5,  10  )')
        assert v.CSS_RGBCOLOR == v.primitiveType
        v = cssutils.css.CSSPrimitiveValue('rgb(1,5,10)')
        assert v.CSS_RGBCOLOR == v.primitiveType
        v = cssutils.css.CSSPrimitiveValue('rgb(1%, .5%, 10.1%)')
        assert v.CSS_RGBCOLOR == v.primitiveType
