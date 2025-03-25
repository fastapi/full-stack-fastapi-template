"""Testcases for cssutils.stylesheets.MediaList"""

import re
import xml.dom

import pytest

import cssutils.stylesheets

from . import basetest


class TestMediaList(basetest.BaseTestCase):
    def setup_method(self):
        self.r = cssutils.stylesheets.MediaList()

    def test_set(self):
        "MediaList.mediaText 1"
        ml = cssutils.stylesheets.MediaList()

        assert 0 == ml.length
        assert 'all' == ml.mediaText

        ml.mediaText = ' print   , screen '
        assert 2 == ml.length
        assert 'print, screen' == ml.mediaText

        # with pytest.raises(xml.dom.InvalidModificationErr, match=self.media_msg('tv')):
        #     ml._setMediaText(u' print , all  , tv ')

        # self.assertEqual(u'all', ml.mediaText)
        # self.assertEqual(1, ml.length)

        with pytest.raises(xml.dom.SyntaxErr):
            ml.appendMedium('test')

    def test_appendMedium(self):
        "MediaList.appendMedium() 1"
        ml = cssutils.stylesheets.MediaList()

        ml.appendMedium('print')
        assert 1 == ml.length
        assert 'print' == ml.mediaText

        ml.appendMedium('screen')
        assert 2 == ml.length
        assert 'print, screen' == ml.mediaText

        # automatic del and append!
        ml.appendMedium('print')
        assert 2 == ml.length
        assert 'screen, print' == ml.mediaText

        # automatic del and append!
        ml.appendMedium('SCREEN')
        assert 2 == ml.length
        assert 'print, SCREEN' == ml.mediaText

        # append invalid MediaQuery
        mq = cssutils.stylesheets.MediaQuery()
        ml.appendMedium(mq)
        assert 2 == ml.length
        assert 'print, SCREEN' == ml.mediaText

        # append()
        mq = cssutils.stylesheets.MediaQuery('tv')
        ml.append(mq)
        assert 3 == ml.length
        assert 'print, SCREEN, tv' == ml.mediaText

        # __setitem__
        with pytest.raises(IndexError):
            ml.__setitem__(10, 'all')
        ml[0] = 'handheld'
        assert 3 == ml.length
        assert 'handheld, SCREEN, tv' == ml.mediaText

    def test_appendAll(self):
        "MediaList.append() 2"
        ml = cssutils.stylesheets.MediaList()
        ml.appendMedium('print')
        ml.appendMedium('tv')
        assert 2 == ml.length
        assert 'print, tv' == ml.mediaText

        ml.appendMedium('all')
        assert 1 == ml.length
        assert 'all' == ml.mediaText

        with pytest.raises(xml.dom.InvalidModificationErr, match=self.media_msg('tv')):
            ml.appendMedium('tv')
        assert 1 == ml.length
        assert 'all' == ml.mediaText

        with pytest.raises(xml.dom.SyntaxErr):
            ml.appendMedium('test')

    @staticmethod
    def media_msg(text):
        return re.escape(
            'MediaList: Ignoring new medium '
            f'cssutils.stylesheets.MediaQuery(mediaText={text!r}) '
            'as already specified "all" (set ``mediaText`` instead).'
        )

    def test_append2All(self):
        "MediaList all"
        ml = cssutils.stylesheets.MediaList()
        ml.appendMedium('all')
        with pytest.raises(
            xml.dom.InvalidModificationErr, match=self.media_msg('print')
        ):
            ml.appendMedium('print')

        sheet = cssutils.parseString('@media all, print { /**/ }')
        assert b'@media all {\n    /**/\n    }' == sheet.cssText

    def test_delete(self):
        "MediaList.deleteMedium()"
        ml = cssutils.stylesheets.MediaList()

        with pytest.raises(xml.dom.NotFoundErr):
            ml.deleteMedium('all')
        with pytest.raises(xml.dom.NotFoundErr):
            ml.deleteMedium('test')

        ml.appendMedium('print')
        ml.deleteMedium('print')
        ml.appendMedium('tV')
        ml.deleteMedium('Tv')
        assert 0 == ml.length
        assert 'all' == ml.mediaText

    def test_item(self):
        "MediaList.item()"
        ml = cssutils.stylesheets.MediaList()
        ml.appendMedium('print')
        ml.appendMedium('screen')

        assert 'print' == ml.item(0)
        assert 'screen' == ml.item(1)
        assert ml.item(2) is None

    def test_mediaText(self):
        "MediaList.mediaText 2"
        tests = {
            'ALL': 'ALL',
            'Tv': 'Tv',
            'all': None,
            'all, handheld': 'all',
            'tv': None,
            'tv, handheld, print': None,
            'tv and (color), handheld and (width: 1px) and (color)': None,
        }
        self.do_equal_r(tests, att='mediaText')

        tests = {
            '': xml.dom.SyntaxErr,
            'UNKNOWN': xml.dom.SyntaxErr,
            'a,b': xml.dom.SyntaxErr,
            'a and (color)': xml.dom.SyntaxErr,
            'not': xml.dom.SyntaxErr,  # known but need media
            'only': xml.dom.SyntaxErr,  # known but need media
            'not tv,': xml.dom.SyntaxErr,  # known but need media
            'all;': xml.dom.SyntaxErr,
            'all, and(color)': xml.dom.SyntaxErr,
            'all,': xml.dom.SyntaxErr,
            'all, ': xml.dom.SyntaxErr,
            'all ,': xml.dom.SyntaxErr,
            'all, /*1*/': xml.dom.SyntaxErr,
            'all and (color),': xml.dom.SyntaxErr,
            'all tv, print': xml.dom.SyntaxErr,
        }
        self.do_raise_r(tests, att='_setMediaText')

    def test_comments(self):
        "MediaList.mediaText comments"
        tests = {
            '/*1*/ tv /*2*/, /*3*/ handheld /*4*/, print': '/*1*/ tv /*2*/ /*3*/, handheld /*4*/, print',
        }
        self.do_equal_r(tests, att='mediaText')

    def test_reprANDstr(self):
        "MediaList.__repr__(), .__str__()"
        mediaText = 'tv, print'

        s = cssutils.stylesheets.MediaList(mediaText=mediaText)

        assert mediaText in str(s)

        s2 = eval(repr(s))
        assert isinstance(s2, s.__class__)
        assert mediaText == s2.mediaText
