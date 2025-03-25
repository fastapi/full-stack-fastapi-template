"""Testcases for cssutils.css.CSSRule"""

import xml.dom

import pytest

import cssutils.css

from . import basetest


class TestCSSRule(basetest.BaseTestCase):
    """
    base class for all CSSRule subclass tests

    overwrite setUp with the appriopriate values, will be used in
    test_init and test_readonly
    overwrite all tests as you please, use::

        super(CLASSNAME, self).test_TESTNAME(params)

    to use the base class tests too
    """

    def setup_method(self):
        """
        self.r is the rule
        self.rRO the readonly rule
        relf.r_type the type as defined in CSSRule
        """
        self._setup_rule()
        self.sheet = cssutils.css.CSSStyleSheet()

    def _setup_rule(self):
        self.r = cssutils.css.CSSRule()
        self.rRO = cssutils.css.CSSRule()
        self.rRO._readonly = True  # must be set here!
        self.r_type = cssutils.css.CSSRule.UNKNOWN_RULE
        self.r_typeString = 'UNKNOWN_RULE'

    def test_init(self):
        "CSSRule.type and init"
        assert self.r_type == self.r.type
        assert self.r_typeString == self.r.typeString
        assert '' == self.r.cssText
        assert self.r.parentRule is None
        assert self.r.parentStyleSheet is None

    def test_parentRule_parentStyleSheet_type(self):  # noqa: C901
        "CSSRule.parentRule .parentStyleSheet .type"
        rules = [
            ('@charset "ascii";', cssutils.css.CSSRule.CHARSET_RULE),
            ('@import "x";', cssutils.css.CSSRule.IMPORT_RULE),
            ('@namespace "x";', cssutils.css.CSSRule.NAMESPACE_RULE),
            ('@font-face { src: url(x) }', cssutils.css.CSSRule.FONT_FACE_RULE),
            (
                '''@media all {
                    @x;
                    a { color: red }
                    /* c  */
                }''',
                cssutils.css.CSSRule.MEDIA_RULE,
            ),
            ('@page :left { color: red }', cssutils.css.CSSRule.PAGE_RULE),
            ('@unknown;', cssutils.css.CSSRule.UNKNOWN_RULE),
            ('b { left: 0 }', cssutils.css.CSSRule.STYLE_RULE),
            ('/*1*/', cssutils.css.CSSRule.COMMENT),  # must be last for add test
        ]
        mrt = [
            cssutils.css.CSSRule.UNKNOWN_RULE,
            cssutils.css.CSSRule.STYLE_RULE,
            cssutils.css.CSSRule.COMMENT,
        ]

        def test(s):
            for i, rule in enumerate(s):
                assert rule.parentRule is None
                assert rule.parentStyleSheet == s
                # self.assertEqual(rule.type, rules[i][1])
                if rule.MEDIA_RULE == rule.type:
                    for j, r in enumerate(rule):
                        assert r.parentRule == rule
                        assert r.parentStyleSheet == s
                        assert r.type == mrt[j]

                if i == 0:  # check encoding
                    assert 'ascii' == s.encoding
                elif i == 2:  # check namespaces
                    assert 'x' == s.namespaces['']

        cssText = ''.join(r[0] for r in rules)
        # parsing
        s = cssutils.parseString(cssText)
        test(s)
        # sheet.cssText
        s = cssutils.css.CSSStyleSheet()
        s.cssText = cssText
        test(s)
        # sheet.add CSS
        s = cssutils.css.CSSStyleSheet()
        for css, _ in rules:
            s.add(css)
        test(s)
        # sheet.insertRule CSS
        s = cssutils.css.CSSStyleSheet()
        for css, _ in rules:
            s.insertRule(css)
        test(s)

        types = [
            cssutils.css.CSSCharsetRule,
            cssutils.css.CSSImportRule,
            cssutils.css.CSSNamespaceRule,
            cssutils.css.CSSFontFaceRule,
            cssutils.css.CSSMediaRule,
            cssutils.css.CSSPageRule,
            cssutils.css.CSSUnknownRule,
            cssutils.css.CSSStyleRule,
            cssutils.css.CSSComment,
        ]
        # sheet.add CSSRule
        s = cssutils.css.CSSStyleSheet()
        for i, (css, _) in enumerate(rules):
            rule = types[i]()
            rule.cssText = css
            s.add(rule)
        test(s)
        # sheet.insertRule CSSRule
        s = cssutils.css.CSSStyleSheet()
        for i, (css, _) in enumerate(rules):
            rule = types[i]()
            rule.cssText = css
            s.insertRule(rule)
        test(s)

    def test_CSSMediaRule_cssRules_parentRule_parentStyleSheet_type(self):
        "CSSMediaRule.cssRules.parentRule .parentStyleSheet .type"
        rules = [
            ('b { left: 0 }', cssutils.css.CSSRule.STYLE_RULE),
            ('/*1*/', cssutils.css.CSSRule.COMMENT),
            ('@x;', cssutils.css.CSSRule.UNKNOWN_RULE),
        ]

        def test(s):
            mr = s.cssRules[0]
            for i, rule in enumerate(mr):
                assert rule.parentRule == mr
                assert rule.parentStyleSheet == s
                assert rule.parentStyleSheet == mr.parentStyleSheet
                assert rule.type == rules[i][1]

        cssText = '@media all { %s }' % ''.join(r[0] for r in rules)
        # parsing
        s = cssutils.parseString(cssText)
        test(s)
        # sheet.cssText
        s = cssutils.css.CSSStyleSheet()
        s.cssText = cssText
        test(s)

        def getMediaSheet():
            s = cssutils.css.CSSStyleSheet()
            s.cssText = '@media all {}'
            return s, s.cssRules[0]

        # sheet.add CSS
        s, mr = getMediaSheet()
        for css, _ in rules:
            mr.add(css)
        test(s)
        # sheet.insertRule CSS
        s, mr = getMediaSheet()
        for css, _ in rules:
            mr.insertRule(css)
        test(s)

        types = [
            cssutils.css.CSSStyleRule,
            cssutils.css.CSSComment,
            cssutils.css.CSSUnknownRule,
        ]
        # sheet.add CSSRule
        s, mr = getMediaSheet()
        for i, (css, _) in enumerate(rules):
            rule = types[i]()
            rule.cssText = css
            mr.add(rule)
        test(s)
        # sheet.insertRule CSSRule
        s, mr = getMediaSheet()
        for i, (css, _) in enumerate(rules):
            rule = types[i]()
            rule.cssText = css
            mr.insertRule(rule)
        test(s)

    def test_readonly(self):
        "CSSRule readonly"
        self.rRO = cssutils.css.CSSRule()
        self.rRO._readonly = True
        assert self.rRO._readonly
        assert '' == self.rRO.cssText
        with pytest.raises(xml.dom.NoModificationAllowedErr):
            self.rRO._setCssText('x')
        assert '' == self.rRO.cssText

    def _test_InvalidModificationErr(self, startwithspace):
        """
        CSSRule.cssText InvalidModificationErr

        called by subclasses

        startwithspace

        for test starting with this not the test but " test" is tested
        e.g. " @page {}"
        exception is the style rule test
        """
        tests = (
            '',
            '/* comment */',
            '@charset "utf-8";',
            '@font-face {}',
            '@import url(x);',
            '@media all {}',
            '@namespace "x";' '@page {}',
            '@unknown;',
            '@variables;',
            # TODO:
            # u'@top-left {}'
            'a style rule {}',
        )
        for test in tests:
            if startwithspace in ('a style rule',) and test in (
                '/* comment */',
                'a style rule {}',
            ):
                continue

            if test.startswith(startwithspace):
                test = ' %s' % test

            with pytest.raises(xml.dom.InvalidModificationErr):
                self.r._setCssText(test)

        # check that type is readonly
        with pytest.raises(AttributeError):
            self.r.__setattr__('parentRule', None)
        with pytest.raises(AttributeError):
            self.r.__setattr__('parentStyleSheet', None)
        with pytest.raises(AttributeError):
            self.r.__setattr__('type', 1)
        with pytest.raises(AttributeError):
            self.r.__setattr__('typeString', "")
