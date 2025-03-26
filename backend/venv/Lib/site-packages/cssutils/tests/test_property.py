"""Testcases for cssutils.css.property._Property."""

import re
import xml.dom

import pytest
from jaraco.test import property_error

import cssutils

from . import basetest


class TestProperty(basetest.BaseTestCase):
    def setup_method(self):
        self.r = cssutils.css.property.Property('top', '1px')  # , 'important')

    def test_init(self):
        "Property.__init__()"
        p = cssutils.css.property.Property('top', '1px')
        assert 'top: 1px' == p.cssText
        assert 'top' == p.literalname
        assert 'top' == p.name
        assert '1px' == p.value
        # self.assertEqual('1px', p.cssValue.cssText)
        assert '1px' == p.propertyValue.cssText
        assert '' == p.priority
        assert p.valid
        assert p.wellformed

        assert ['top'] == p.seqs[0]
        assert isinstance(cssutils.css.PropertyValue(cssText="2px"), type(p.seqs[1]))
        assert [] == p.seqs[2]

        assert p.valid

        # Prop of MediaQuery
        p = cssutils.css.property.Property('top', _mediaQuery=True)
        assert 'top' == p.cssText
        assert 'top' == p.literalname
        assert 'top' == p.name
        assert '' == p.value
        # self.assertEqual('', p.cssValue.cssText)
        assert '' == p.propertyValue.cssText
        assert '' == p.priority
        assert not p.valid
        # p.cssValue.cssText = '1px'
        p.propertyValue.cssText = '1px'
        assert 'top: 1px' == p.cssText
        # p.cssValue = ''
        p.propertyValue = ''
        assert 'top' == p.cssText

        with pytest.raises(xml.dom.SyntaxErr):
            cssutils.css.property.Property('top', '')
        with pytest.raises(xml.dom.SyntaxErr):
            cssutils.css.property.Property('top')
        p = cssutils.css.property.Property('top', '0')
        assert '0' == p.value
        assert p.wellformed
        with pytest.raises(xml.dom.SyntaxErr):
            p._setValue('')
        assert '0' == p.value
        assert p.wellformed

    def test_cssText(self):
        "Property.cssText"
        p = cssutils.css.property.Property()

        tests = {
            'a: 1': None,
            'a: 1px 2px': None,
            'a: 1 !important': None,
            'a: 1 !IMPORTANT': 'a: 1 !important',
            'a: 1 !impor\\tant': 'a: 1 !important',
            # TODO: important with unicode escapes!
            'font: normal 1em/1.5 serif': None,
            'font: normal 1em/serif': None,
        }
        self.do_equal_r(tests)

        tests = {
            '': (xml.dom.SyntaxErr, 'Property: No property name found: '),
            ':': (xml.dom.SyntaxErr, 'Property: No property name found: : [1:1: :]'),
            'a': (xml.dom.SyntaxErr, 'Property: No ":" after name found: a [1:1: a]'),
            'b !': (
                xml.dom.SyntaxErr,
                'Property: No ":" after name found: b ! [1:3: !]',
            ),
            '/**/x': (
                xml.dom.SyntaxErr,
                'Property: No ":" after name found: /**/x [1:5: x]',
            ),
            'c:': (xml.dom.SyntaxErr, "Property: No property value found: c: [1:2: :]"),
            'd: ': (xml.dom.SyntaxErr, "No content to parse."),
            'e:!important': (xml.dom.SyntaxErr, "No content to parse."),
            'f: 1!': (xml.dom.SyntaxErr, 'Property: Invalid priority: !'),
            'g: 1!importantX': (
                xml.dom.SyntaxErr,
                "Property: No CSS priority value: importantx",
            ),
            # TODO?
            # u'a: 1;': (xml.dom.SyntaxErr,
            #       u'''CSSValue: No match: ('CHAR', u';', 1, 5)''')
        }
        for test in tests:
            ecp, msg = tests[test]
            with pytest.raises(ecp, match=re.escape(msg)):
                p._setCssText(test)

    def test_name(self):
        "Property.name"
        p = cssutils.css.property.Property('top', '1px')
        p.name = 'left'
        assert 'left' == p.name

        tests = {
            'top': None,
            ' top': 'top',
            'top ': 'top',
            ' top ': 'top',
            '/*x*/ top ': 'top',
            ' top /*x*/': 'top',
            '/*x*/top/*x*/': 'top',
            '\\x': 'x',
            'a\\010': 'a\x10',
            'a\\01': 'a\x01',
        }
        self.do_equal_r(tests, att='name')

        tests = {
            '': xml.dom.SyntaxErr,
            ' ': xml.dom.SyntaxErr,
            '"\n': xml.dom.SyntaxErr,
            '/*x*/': xml.dom.SyntaxErr,
            ':': xml.dom.SyntaxErr,
            ';': xml.dom.SyntaxErr,
            'top:': xml.dom.SyntaxErr,
            'top;': xml.dom.SyntaxErr,
            'color: #xyz': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests, att='_setName')

        p = cssutils.css.property.Property(r'c\olor', 'red')
        assert r'c\olor' == p.literalname
        assert 'color' == p.name

    def test_literalname(self):
        "Property.literalname"
        p = cssutils.css.property.Property(r'c\olor', 'red')
        assert r'c\olor' == p.literalname
        with pytest.raises(
            AttributeError, match=property_error("Property.literalname")
        ):
            p.literalname = 'color'

    def test_validate(self):
        "Property.valid"
        p = cssutils.css.property.Property('left', '1px', '')

        assert p.valid

        p.name = 'color'
        assert p.valid is False

        p.name = 'top'
        assert p.valid

        p.value = 'red'
        assert p.valid is False

    def test_priority(self):
        "Property.priority"
        p = cssutils.css.property.Property('top', '1px', 'important')

        for prio in (None, ''):
            p.priority = prio
            assert '' == p.priority
            assert '' == p.literalpriority

        for prio in (
            '!important',
            '! important',
            '!/* x */ important',
            '!/* x */ important /**/',
            'important',
            'IMPORTANT',
            r'im\portant',
        ):
            p.priority = prio
            assert 'important' == p.priority
            if prio.startswith('!'):
                prio = prio[1:].strip()
            if '/*' in prio:
                check = 'important'
            else:
                check = prio
            assert check == p.literalpriority

        tests = {
            ' ': xml.dom.SyntaxErr,
            '"\n': xml.dom.SyntaxErr,
            # u'important': xml.dom.SyntaxErr,
            ';': xml.dom.SyntaxErr,
            '!important !important': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests, att='_setPriority')

    def test_value(self):
        "Property.value"
        p = cssutils.css.property.Property('top', '1px')
        assert '1px' == p.value
        p.value = '2px'
        assert '2px' == p.value

        tests = {
            '1px': None,
            ' 2px': '2px',
            '3px ': '3px',
            ' 4px ': '4px',
            '5px 1px': '5px 1px',
        }
        self.do_equal_r(tests, att='value')

        tests = {
            # no value
            None: xml.dom.SyntaxErr,
            '': xml.dom.SyntaxErr,
            ' ': xml.dom.SyntaxErr,
            '"\n': xml.dom.SyntaxErr,
            '/*x*/': xml.dom.SyntaxErr,
            # not allowed:
            ':': xml.dom.SyntaxErr,
            ';': xml.dom.SyntaxErr,
            '!important': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests, att='_setValue')

    def test_reprANDstr(self):
        "Property.__repr__(), .__str__()"
        name = "color"
        value = "red"
        priority = "important"

        s = cssutils.css.property.Property(name=name, value=value, priority=priority)

        assert name in str(s)
        assert value in str(s)
        assert priority in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert name == s2.name
        assert value == s2.value
        assert priority == s2.priority
