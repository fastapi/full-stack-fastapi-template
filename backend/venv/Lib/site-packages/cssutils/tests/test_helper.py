"""Testcases for cssutils.helper"""

from cssutils.helper import normalize, string, stringvalue, uri, urivalue


class TestHelper:
    def test_normalize(self):
        "helper._normalize()"
        tests = {
            'abcdefg ABCDEFG äöüß€ AÖÜ': r'abcdefg abcdefg äöüß€ aöü',
            r'\ga\Ga\\\ ': r'gaga\ ',
            r'0123456789': r'0123456789',
            r'"\x"': r'"x"',
            # unicode escape seqs should have been done by
            # the tokenizer...
        }
        for test, exp in list(tests.items()):
            assert normalize(test) == exp
            # static too
            assert normalize(test) == exp

    def test_string(self):
        "helper.string()"
        assert '"x"' == string('x')
        assert '"1 2ä€"' == string('1 2ä€')
        assert r'''"'"''' == string("'")
        assert r'"\""' == string('"')
        # \n = 0xa, \r = 0xd, \f = 0xc
        assert r'"\a "' == string(
            '''
'''
        )
        assert r'"\c "' == string('\f')
        assert r'"\d "' == string('\r')
        assert r'"\d \a "' == string('\r\n')

    def test_stringvalue(self):
        "helper.stringvalue()"
        assert 'x' == stringvalue('"x"')
        assert '"' == stringvalue('"\\""')
        assert r'x' == stringvalue(r"\x ")

        # escapes should have been done by tokenizer
        # so this shoule not happen at all:
        assert r'a' == stringvalue(r"\a ")

    def test_uri(self):
        "helper.uri()"
        assert 'url(x)' == uri('x')
        assert 'url("(")' == uri('(')
        assert 'url(")")' == uri(')')
        assert 'url(" ")' == uri(' ')
        assert 'url(";")' == uri(';')
        assert 'url(",")' == uri(',')
        assert 'url("x)x")' == uri('x)x')

    def test_urivalue(self):
        "helper.urivalue()"
        assert 'x' == urivalue('url(x)')
        assert 'x' == urivalue('url("x")')
        assert ')' == urivalue('url(")")')
