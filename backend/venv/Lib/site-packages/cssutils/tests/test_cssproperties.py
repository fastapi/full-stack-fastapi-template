"""Testcases for cssutils.css.cssproperties."""

import pytest

import cssutils.css
import cssutils.profiles


class TestCSSProperties:
    def test_toDOMname(self):
        "cssproperties _toDOMname(CSSname)"
        _toDOMname = cssutils.css.cssproperties._toDOMname

        assert 'color' == _toDOMname('color')
        assert 'fontStyle' == _toDOMname('font-style')
        assert 'MozOpacity' == _toDOMname('-moz-opacity')
        assert 'UNKNOWN' == _toDOMname('UNKNOWN')
        assert 'AnUNKNOWN' == _toDOMname('-anUNKNOWN')

    def test_toCSSname(self):
        "cssproperties _toCSSname(DOMname)"
        _toCSSname = cssutils.css.cssproperties._toCSSname

        assert 'color' == _toCSSname('color')
        assert 'font-style' == _toCSSname('fontStyle')
        assert '-moz-opacity' == _toCSSname('MozOpacity')
        assert 'UNKNOWN' == _toCSSname('UNKNOWN')
        assert '-anUNKNOWN' == _toCSSname('AnUNKNOWN')

    def test_CSS2Properties(self):
        "CSS2Properties"
        CSS2Properties = cssutils.css.cssproperties.CSS2Properties
        assert isinstance(property(), type(CSS2Properties.color))
        assert sum(len(x) for x in list(cssutils.profiles.properties.values())) == len(
            CSS2Properties._properties
        )

        c2 = CSS2Properties()
        # CSS2Properties has simplified implementation return always None
        assert c2.color is None
        assert c2.__setattr__('color', 1) is None
        assert c2.__delattr__('color') is None
        # only defined properties
        with pytest.raises(AttributeError):
            c2.__getattribute__('UNKNOWN')
