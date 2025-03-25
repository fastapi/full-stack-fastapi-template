"""Testcases for cssutils.css.CSSRuleList"""

import pytest

import cssutils


class TestCSSRuleList:
    def test_init(self):
        "CSSRuleList.__init__()"
        r = cssutils.css.CSSRuleList()
        assert 0 == r.length
        assert r.item(2) is None

        # subclasses list but all setting options like append, extend etc
        # need to be added to an instance of this class by a using class!
        with pytest.raises(NotImplementedError):
            r.append(1)

    def test_rulesOfType(self):
        "CSSRuleList.rulesOfType()"
        s = cssutils.parseString(
            '''
        /*c*/
        @namespace "a";
        a { color: red}
        b { left: 0 }'''
        )

        c = list(s.cssRules.rulesOfType(cssutils.css.CSSRule.COMMENT))
        assert 1 == len(c)
        assert '/*c*/' == c[0].cssText

        r = list(s.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE))
        assert 2 == len(r)
        assert 'b {\n    left: 0\n    }' == r[1].cssText
