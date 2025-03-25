"""Base class for all tests"""

import sys

import pytest

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

import cssutils


def get_sheet_filename(sheet_name):
    """Get the filename for the given sheet."""
    return resources.files('cssutils') / 'tests' / 'sheets' / sheet_name


class BaseTestCase:
    @staticmethod
    def do_equal_p(tests, att='cssText', raising=True):
        p = cssutils.CSSParser(raiseExceptions=raising)
        # parse and check att of result
        for test, expected in tests.items():
            s = p.parseString(test)
            if expected is None:
                expected = test
            assert str(s.__getattribute__(att), 'utf-8') == expected

    @staticmethod
    def do_raise_p(tests, raising=True):
        # parse and expect raise
        p = cssutils.CSSParser(raiseExceptions=raising)
        for test, expected in tests.items():
            with pytest.raises(expected):
                p.parseString(test)

    def do_equal_r(self, tests, att='cssText'):
        # set attribute att of self.r and assert Equal
        for test, expected in tests.items():
            self.r.__setattr__(att, test)
            if expected is None:
                expected = test
            assert self.r.__getattribute__(att) == expected

    def do_raise_r(self, tests, att='_setCssText'):
        # set self.r and expect raise
        for test, expected in tests.items():
            with pytest.raises(expected):
                self.r.__getattribute__(att)(test)

    def do_raise_r_list(self, tests, err, att='_setCssText'):
        # set self.r and expect raise
        for test in tests:
            with pytest.raises(err):
                self.r.__getattribute__(att)(test)
