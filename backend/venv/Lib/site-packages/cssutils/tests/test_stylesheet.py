"""Testcases for cssutils.stylesheets.StyleSheet"""

import cssutils


class TestStyleSheet:
    def test_init(self):
        "StyleSheet.__init__()"
        s = cssutils.stylesheets.StyleSheet()

        assert s.type == 'text/css'
        assert s.href is None
        assert s.media is None
        assert s.title == ''
        assert s.ownerNode is None
        assert s.parentStyleSheet is None
        assert s.alternate is False
        assert s.disabled is False

        s = cssutils.stylesheets.StyleSheet(
            type='unknown',
            href='test.css',
            media=None,
            title='title',
            ownerNode=None,
            parentStyleSheet=None,
            alternate=True,
            disabled=True,
        )

        assert s.type == 'unknown'
        assert s.href == 'test.css'
        assert s.media is None
        assert s.title == 'title'
        assert s.ownerNode is None
        assert s.parentStyleSheet is None
        assert s.alternate
        assert s.disabled
