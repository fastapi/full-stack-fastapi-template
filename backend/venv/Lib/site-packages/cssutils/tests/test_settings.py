"""Testcases for cssutils.settings"""

import cssutils
import cssutils.settings


class TestSettings:
    def test_set(self):
        "settings.set()"
        cssutils.ser.prefs.useMinified()
        text = (
            'a {filter: progid:DXImageTransform.Microsoft.BasicImage( rotation = 90 )}'
        )

        assert cssutils.parseString(text).cssText == b''

        cssutils.settings.set('DXImageTransform.Microsoft', True)
        assert (
            cssutils.parseString(text).cssText
            == b'a{filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=90)}'
        )
