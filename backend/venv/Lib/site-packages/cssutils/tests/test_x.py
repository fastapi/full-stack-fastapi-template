"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""

import xml.dom

import pytest

import cssutils


class TestX:
    @pytest.mark.xfail(reason="not implemented")
    def test_priority(self):
        "Property.priority"
        s = cssutils.parseString('a { color: red }')
        assert s.cssText == b'a {\n    color: red\n    }'

        assert '' == s.cssRules[0].style.getPropertyPriority('color')

        s = cssutils.parseString('a { color: red !important }')
        assert 'a {\n    color: red !important\n    }' == s.cssText
        assert 'important' == s.cssRules[0].style.getPropertyPriority('color')

        cssutils.log.raiseExceptions = True
        p = cssutils.css.Property('color', 'red', '')
        assert p.priority == ''
        p = cssutils.css.Property('color', 'red', '!important')
        assert p.priority == 'important'
        with pytest.raises(xml.dom.SyntaxErr):
            cssutils.css.Property('color', 'red', 'x')

        cssutils.log.raiseExceptions = False
        p = cssutils.css.Property('color', 'red', '!x')
        assert p.priority == 'x'
        p = cssutils.css.Property('color', 'red', '!x')
        assert p.priority == 'x'
        cssutils.log.raiseExceptions = True

        # invalid but kept!
        # cssutils.log.raiseExceptions = False
        s = cssutils.parseString('a { color: red !x }')
        assert 'a {\n    color: red !x\n    }' == s.cssText
        assert 'x' == s.cssRules[0].style.getPropertyPriority('color')
