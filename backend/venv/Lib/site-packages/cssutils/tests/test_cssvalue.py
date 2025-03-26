"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""

import xml.dom

import pytest

import cssutils

from . import basetest

pytestmark = pytest.mark.xfail(reason="incomplete")


class TestCSSValue(basetest.BaseTestCase):
    def setup_method(self):
        self.r = cssutils.css.CSSValue()  # needed for tests

    def test_init(self):
        "CSSValue.__init__()"
        v = cssutils.css.CSSValue()
        assert '' == v.cssText
        assert None is v.cssValueType
        assert None is v.cssValueTypeString

    def test_escapes(self):
        "CSSValue Escapes"
        v = cssutils.css.CSSValue()
        v.cssText = '1px'
        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert v.CSS_PX == v.primitiveType
        assert '1px' == v.cssText

        v.cssText = '1PX'
        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert v.CSS_PX == v.primitiveType
        assert '1px' == v.cssText

        v.cssText = '1p\\x'
        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert v.CSS_PX == v.primitiveType
        assert '1px' == v.cssText

    def test_cssText(self):
        "CSSValue.cssText"
        v = cssutils.css.CSSValue()
        v.cssText = '1px'
        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert v.CSS_PX == v.primitiveType
        assert '1px' == v.cssText

        v = cssutils.css.CSSValue()
        v.cssText = '1px'
        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert v.CSS_PX == v.primitiveType
        assert '1px' == v.cssText

        v = cssutils.css.CSSValue()
        v.cssText = 'a  ,b,  c  ,"d or d", "e, " '
        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert v.CSS_STRING == v.primitiveType
        assert 'a, b, c, "d or d", "e, "' == v.cssText

        v.cssText = '  1   px    '
        assert v.CSS_VALUE_LIST == v.cssValueType
        assert '1 px' == v.cssText

        v.cssText = '  normal 1px a, b, "c" end   '
        assert v.CSS_VALUE_LIST == v.cssValueType
        assert 'normal 1px a, b, "c" end' == v.cssText

        for x in v:
            assert x.CSS_PRIMITIVE_VALUE == x.cssValueType
            if x == 0:
                assert x.CSS_IDENT == x.primitiveType
                assert 'normal' == x.cssText
            elif x == 1:
                assert x.CSS_PX == x.primitiveType
                assert '1px' == x.cssText
            if x == 2:
                assert x.CSS_STRING == x.primitiveType
                assert 'a, b, "c"' == x.cssText
            if x == 3:
                assert x.CSS_IDENT == x.primitiveType
                assert 'end' == x.cssText

        v = cssutils.css.CSSValue()
        v.cssText = '  1   px    '
        assert v.CSS_VALUE_LIST == v.cssValueType
        assert '1 px' == v.cssText

        v.cssText = 'expression(document.body.clientWidth > 972 ? "1014px": "100%" )'
        assert v.CSS_PRIMITIVE_VALUE == v.cssValueType
        assert v.CSS_UNKNOWN == v.primitiveType
        assert (
            'expression(document.body.clientWidth > 972?"1014px": "100%")' == v.cssText
        )

    def test_cssText2(self):
        "CSSValue.cssText 2"
        tests = {
            # mix
            'a()1,-1,+1,1%,-1%,1px,-1px,"a",a,url(a),#aabb44': 'a() 1, -1, 1, 1%, -1%, 1px, -1px, "a", a, url(a), #ab4',
            # S or COMMENT
            'red': 'red',
            'red ': 'red',
            ' red ': 'red',
            '/**/red': '/**/ red',
            'red/**/': 'red /**/',
            '/**/red/**/': '/**/ red /**/',
            '/**/ red': '/**/ red',
            'red /**/': 'red /**/',
            '/**/ red /**/': '/**/ red /**/',
            'red-': 'red-',
            # num / dimension
            '.0': '0',
            '0': '0',
            '0.0': '0',
            '00': '0',
            '0%': '0%',
            '0px': '0',
            '-.0': '0',
            '-0': '0',
            '-0.0': '0',
            '-00': '0',
            '-0%': '0%',
            '-0px': '0',
            '+.0': '0',
            '+0': '0',
            '+0.0': '0',
            '+00': '0',
            '+0%': '0%',
            '+0px': '0',
            '1': '1',
            '1.0': '1',
            '1px': '1px',
            '1%': '1%',
            '1px1': '1px1',
            '+1': '1',
            '-1': '-1',
            '+1.0': '1',
            '-1.0': '-1',
            # string, escaped nl is removed during tokenizing
            '"x"': '"x"',
            "'x'": '"x"',
            # ur''' "1\'2" ''': u'''"1'2"''', #???
            # ur"'x\"'": ur'"x\""', #???
            r'''"x\
y"''': '''"xy"''',
            # hash and rgb/a
            '#112234': '#112234',
            '#112233': '#123',
            'rgb(1,2,3)': 'rgb(1, 2, 3)',
            'rgb(  1  ,  2  ,  3  )': 'rgb(1, 2, 3)',
            'rgb(-1,+2,0)': 'rgb(-1, 2, 0)',
            'rgba(1,2,3,4)': 'rgba(1, 2, 3, 4)',
            'rgba(  1  ,  2  ,  3  ,  4 )': 'rgba(1, 2, 3, 4)',
            'rgba(-1,+2,0, 0)': 'rgba(-1, 2, 0, 0)',
            # FUNCTION
            'f(1,2)': 'f(1, 2)',
            'f(  1  ,  2  )': 'f(1, 2)',
            'f(-1,+2)': 'f(-1, 2)',
            'f(  -1  ,  +2  )': 'f(-1, 2)',
            'fun(  -1  ,  +2  )': 'fun(-1, 2)',
            'local( x )': 'local(x)',
            'test(1px, #111, y, 1, 1%, "1", y(), var(x))': 'test(1px, #111, y, 1, 1%, "1", y(), var(x))',
            'test(-1px, #111, y, -1, -1%, "1", -y())': 'test(-1px, #111, y, -1, -1%, "1", -y())',
            'url(y)  format( "x" ,  "y" )': 'url(y) format("x", "y")',
            'f(1 2,3 4)': 'f(1 2, 3 4)',
            # IE expression
            r'Expression()': 'Expression()',
            r'expression(-1 < +2)': 'expression(-1< + 2)',
            r'expression(document.width == "1")': 'expression(document.width=="1")',
            'alpha(opacity=80)': 'alpha(opacity=80)',
            'alpha( opacity = 80 , x=2  )': 'alpha(opacity=80, x=2)',
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

        tests = {
            'a+': xml.dom.SyntaxErr,
            '-': xml.dom.SyntaxErr,
            '+': xml.dom.SyntaxErr,
            '-%': xml.dom.SyntaxErr,
            '+a': xml.dom.SyntaxErr,
            '--1px': xml.dom.SyntaxErr,
            '++1px': xml.dom.SyntaxErr,
            '#': xml.dom.SyntaxErr,
            '#00': xml.dom.SyntaxErr,
            '#0000': xml.dom.SyntaxErr,
            '#00000': xml.dom.SyntaxErr,
            '#0000000': xml.dom.SyntaxErr,
            '-#0': xml.dom.SyntaxErr,
            # operator
            ',': xml.dom.SyntaxErr,
            '1,,2': xml.dom.SyntaxErr,
            '1,/**/,2': xml.dom.SyntaxErr,
            '1  ,  /**/  ,  2': xml.dom.SyntaxErr,
            '1,': xml.dom.SyntaxErr,
            '1, ': xml.dom.SyntaxErr,
            '1 ,': xml.dom.SyntaxErr,
            '1 , ': xml.dom.SyntaxErr,
            '1  ,  ': xml.dom.SyntaxErr,
            '1//2': xml.dom.SyntaxErr,
            # URL
            'url(x))': xml.dom.SyntaxErr,
            # string
            '"': xml.dom.SyntaxErr,
            "'": xml.dom.SyntaxErr,
            # function
            'f(-)': xml.dom.SyntaxErr,
            'f(x))': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests)

    def test_incomplete(self):
        "CSSValue (incomplete)"
        tests = {'url("a': 'url(a)', 'url(a': 'url(a)'}
        for v, exp in list(tests.items()):
            s = cssutils.parseString('a { background: %s' % v)
            v = s.cssRules[0].style.background
            assert v == exp

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

    def test_readonly(self):
        "(CSSValue._readonly)"
        v = cssutils.css.CSSValue(cssText='inherit')
        assert False is v._readonly

        v = cssutils.css.CSSValue(cssText='inherit', readonly=True)
        assert True is v._readonly
        assert 'inherit', v.cssText
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            v._setCssText('x')
        assert 'inherit', v.cssText

    def test_reprANDstr(self):
        "CSSValue.__repr__(), .__str__()"
        cssText = 'inherit'

        s = cssutils.css.CSSValue(cssText=cssText)

        assert cssText in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert cssText == s2.cssText


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
                    "CSSPrimitiveValue: Cannot coerce "
                    "primitiveType 'CSS_NUMBER' to 'CSS_EMS'",
                ),
                (
                    V.CSS_EXS,
                    1,
                    xml.dom.InvalidAccessErr,
                    "CSSPrimitiveValue: Cannot coerce primitiveType "
                    "'CSS_NUMBER' to 'CSS_EXS'",
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
                if type(exp) == type or type(exp) == type:  # 2.4 compatibility
                    if cssText:
                        with pytest.raises(exp, match=cssText):
                            pv.setFloatValue(setType, setValue)
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
        assert r'"' == v.getStringValue()
        assert (r'"', 'URI') == v._value

        v.setStringValue(v.CSS_URI, "''")
        assert r"''" == v.getStringValue()
        assert (r"''", 'URI') == v._value

        v.setStringValue(v.CSS_URI, ',')
        assert r',' == v.getStringValue()
        assert (r',', 'URI') == v._value

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

    def test_reprANDstr(self):
        "CSSPrimitiveValue.__repr__(), .__str__()"
        v = '111'

        s = cssutils.css.CSSPrimitiveValue(v)

        assert v in str(s)
        assert 'CSS_NUMBER' in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert v == s2.cssText


class TestCSSValueList:
    def test_init(self):
        "CSSValueList.__init__()"
        v = cssutils.css.CSSValue(cssText='red blue')
        assert v.CSS_VALUE_LIST == v.cssValueType
        assert 'red blue' == v.cssText

        assert 2 == v.length

        item = v.item(0)
        item.setStringValue(item.CSS_IDENT, 'green')
        assert 'green blue' == v.cssText

    def test_numbers(self):
        "CSSValueList.cssText"
        tests = {
            '0 0px -0px +0px': ('0 0 0 0', 4),
            '1 2 3 4': (None, 4),
            '-1 -2 -3 -4': (None, 4),
            '-1 2': (None, 2),
            '-1px red "x"': (None, 3),
            'a, b c': (None, 2),
            '1px1 2% 3': ('1px1 2% 3', 3),
            'f(+1pX, -2, 5%) 1': ('f(1px, -2, 5%) 1', 2),
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
        for test in tests:
            exp, num = tests[test]
            if not exp:
                exp = test
            v = cssutils.css.CSSValue(cssText=test)
            assert v.CSS_VALUE_LIST == v.cssValueType
            assert num == v.length
            assert exp == v.cssText

    def test_reprANDstr(self):
        "CSSValueList.__repr__(), .__str__()"
        v = '1px 2px'

        s = cssutils.css.CSSValue(v)
        assert isinstance(s, cssutils.css.CSSValueList)

        assert 'length=2' in str(s)
        assert v in str(s)

        # not "eval()"able!
        # s2 = eval(repr(s))
