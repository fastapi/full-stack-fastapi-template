"""Testcases for cssutils.css.selectorlist.SelectorList."""

import xml.dom

import pytest

import cssutils
from cssutils.css.selectorlist import SelectorList

from . import basetest


class TestSelectorList(basetest.BaseTestCase):
    def setup_method(self):
        self.r = SelectorList()

    def test_init(self):
        "SelectorList.__init__() and .length"
        s = SelectorList()
        assert 0 == s.length

        s = SelectorList('a, b')
        assert 2 == s.length
        assert 'a, b' == s.selectorText

        s = SelectorList(selectorText='a')
        assert 1 == s.length
        assert 'a' == s.selectorText

        s = SelectorList(selectorText=('p|a', {'p': 'uri'}))  # n-dict
        assert 1 == s.length
        assert 'p|a' == s.selectorText

        s = SelectorList(selectorText=('p|a', (('p', 'uri'),)))  # n-tuples
        assert 1 == s.length
        assert 'p|a' == s.selectorText

    def test_parentRule(self):
        "Selector.parentRule"

        def check(style):
            assert style == style.selectorList.parentRule
            for sel in style.selectorList:
                assert style.selectorList == sel.parent

        style = cssutils.css.CSSStyleRule('a, b')
        check(style)

        # add new selector
        style.selectorList.append(cssutils.css.Selector('x'))
        check(style)

        # replace selectorList
        style.selectorList = cssutils.css.SelectorList('x')
        check(style)

        # replace selectorText
        style.selectorText = 'x, y'
        check(style)

    def test_appendSelector(self):
        "SelectorList.appendSelector() and .length"
        s = SelectorList()
        s.appendSelector('a')
        assert 1 == s.length

        with pytest.raises(xml.dom.InvalidModificationErr):
            s.appendSelector('b,')
        assert 1 == s.length

        assert 'a' == s.selectorText

        s.append('b')
        assert 2 == s.length
        assert 'a, b' == s.selectorText

        s.append('a')
        assert 2 == s.length
        assert 'b, a' == s.selectorText

        # __setitem__
        with pytest.raises(IndexError):
            s.__setitem__(4, 'x')
        s[1] = 'c'
        assert 2 == s.length
        assert 'b, c' == s.selectorText
        # TODO: remove duplicates?
        #        s[0] = 'c'
        #        self.assertEqual(1, s.length)
        #        self.assertEqual(u'c', s.selectorText)

        s = SelectorList()
        s.appendSelector(('p|a', {'p': 'uri', 'x': 'xxx'}))
        assert 'p|a' == s.selectorText
        # x gets lost as not used
        with pytest.raises(xml.dom.NamespaceErr):
            s.append('x|a')
        # not set at all
        with pytest.raises(xml.dom.NamespaceErr):
            s.append('y|a')
        # but p is retained
        s.append('p|b')
        assert 'p|a, p|b' == s.selectorText

    def test_selectorText(self):
        "SelectorList.selectorText"
        s = SelectorList()
        s.selectorText = 'a, b'
        assert 'a, b' == s.selectorText
        with pytest.raises(xml.dom.SyntaxErr):
            s._setSelectorText(',')
        # not changed as invalid!
        assert 'a, b' == s.selectorText

        tests = {
            '*': None,
            '/*1*/*': None,
            '/*1*/*, a': None,
            'a, b': None,
            'a ,b': 'a, b',
            'a , b': 'a, b',
            'a, b, c': 'a, b, c',
            '#a, x#a, .b, x.b': '#a, x#a, .b, x.b',
            ('[p|a], p|*', (('p', 'uri'),)): '[p|a], p|*',
        }
        # do not parse as not complete
        self.do_equal_r(tests, att='selectorText')

        tests = {
            'x|*': xml.dom.NamespaceErr,
            '': xml.dom.SyntaxErr,
            ' ': xml.dom.SyntaxErr,
            ',': xml.dom.SyntaxErr,
            'a,': xml.dom.SyntaxErr,
            ',a': xml.dom.SyntaxErr,
            '/* 1 */,a': xml.dom.SyntaxErr,
        }
        # only set as not complete
        self.do_raise_r(tests, att='_setSelectorText')

    def test_reprANDstr(self):
        "SelectorList.__repr__(), .__str__()"
        sel = ('a, p|b', {'p': 'uri'})

        s = cssutils.css.SelectorList(selectorText=sel)

        assert sel[0] in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert sel[0] == s2.selectorText
