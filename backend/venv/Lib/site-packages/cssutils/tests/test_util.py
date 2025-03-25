"""Testcases for cssutils.util"""

import re
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message
from unittest import mock

import pytest

from cssutils.util import Base, LazyRegex, ListSeq, _defaultFetcher, _readUrl


class TestListSeq:
    def test_all(self):
        "util.ListSeq"
        ls = ListSeq()
        assert 0 == len(ls)
        # append()
        with pytest.raises(NotImplementedError):
            ls.append(1)
        # set
        with pytest.raises(NotImplementedError):
            ls.__setitem__(0, 1)

        # hack:
        ls.seq.append(1)
        ls.seq.append(2)

        # len
        assert 2 == len(ls)
        # __contains__
        assert True is (1 in ls)
        # get
        assert 1 == ls[0]
        assert 2 == ls[1]
        # del
        del ls[0]
        assert 1 == len(ls)
        assert False is (1 in ls)
        # for in
        for x in ls:
            assert 2 == x


class TestBase:
    def test_normalize(self):
        "Base._normalize()"
        b = Base()
        tests = {
            'abcdefg ABCDEFG äöüß€ AÖÜ': 'abcdefg abcdefg äöüß€ aöü',
            r'\ga\Ga\\\ ': r'gaga\ ',
            r'0123456789': '0123456789',
            # unicode escape seqs should have been done by
            # the tokenizer...
        }
        for test, exp in list(tests.items()):
            assert b._normalize(test) == exp
            # static too
            assert Base._normalize(test) == exp

    def test_tokenupto(self):  # noqa: C901
        "Base._tokensupto2()"

        # tests nested blocks of {} [] or ()
        b = Base()

        tests = [
            ('default', 'a[{1}]({2}) { } NOT', 'a[{1}]({2}) { }', False),
            ('default', 'a[{1}]({2}) { } NOT', 'a[{1}]func({2}) { }', True),
            ('blockstartonly', 'a[{1}]({2}) { NOT', 'a[{1}]({2}) {', False),
            ('blockstartonly', 'a[{1}]({2}) { NOT', 'a[{1}]func({2}) {', True),
            ('propertynameendonly', 'a[(2)1] { }2 : a;', 'a[(2)1] { }2 :', False),
            ('propertynameendonly', 'a[(2)1] { }2 : a;', 'a[func(2)1] { }2 :', True),
            (
                'propertyvalueendonly',
                'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1;',
                False,
            ),
            (
                'propertyvalueendonly',
                'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                'a{;{;}[;]func(;)}[;{;}[;]func(;)]func(;{;}[;]func(;)) 1;',
                True,
            ),
            (
                'funcendonly',
                'a{[1]}([3])[{[1]}[2]([3])]) NOT',
                'a{[1]}([3])[{[1]}[2]([3])])',
                False,
            ),
            (
                'funcendonly',
                'a{[1]}([3])[{[1]}[2]([3])]) NOT',
                'a{[1]}func([3])[{[1]}[2]func([3])])',
                True,
            ),
            (
                'selectorattendonly',
                '[a[()]{()}([()]{()}())] NOT',
                '[a[()]{()}([()]{()}())]',
                False,
            ),
            (
                'selectorattendonly',
                '[a[()]{()}([()]{()}())] NOT',
                '[a[func()]{func()}func([func()]{func()}func())]',
                True,
            ),
            # issue 50
            ('withstarttoken [', 'a];x', '[a];', False),
        ]

        for typ, values, exp, paransasfunc in tests:

            def maketokens(valuelist):
                # returns list of tuples
                return [('TYPE', v, 0, 0) for v in valuelist]

            tokens = maketokens(list(values))
            if paransasfunc:
                for i, t in enumerate(tokens):
                    if '(' == t[1]:
                        tokens[i] = ('FUNCTION', 'func(', t[2], t[3])

            if 'default' == typ:
                restokens = b._tokensupto2(tokens)
            elif 'blockstartonly' == typ:
                restokens = b._tokensupto2(tokens, blockstartonly=True)
            elif 'propertynameendonly' == typ:
                restokens = b._tokensupto2(tokens, propertynameendonly=True)
            elif 'propertyvalueendonly' == typ:
                restokens = b._tokensupto2(tokens, propertyvalueendonly=True)
            elif 'funcendonly' == typ:
                restokens = b._tokensupto2(tokens, funcendonly=True)
            elif 'selectorattendonly' == typ:
                restokens = b._tokensupto2(tokens, selectorattendonly=True)
            elif 'withstarttoken [' == typ:
                restokens = b._tokensupto2(tokens, ('CHAR', '[', 0, 0))

            res = ''.join([t[1] for t in restokens])
            assert exp == res


class Test_readUrl:
    """needs mock"""

    def test_readUrl(self):
        """util._readUrl()"""
        # for additional tests see test_parse.py
        url = 'http://example.com/test.css'

        def make_fetcher(r):
            # normally r == encoding, content
            def fetcher(url):
                return r

            return fetcher

        tests = {
            # defaultFetcher returns: readUrl returns
            None: (None, None, None),
            (None, ''): ('utf-8', 5, ''),
            (None, '€'.encode()): ('utf-8', 5, '€'),
            ('utf-8', '€'.encode()): ('utf-8', 1, '€'),
            ('ISO-8859-1', 'ä'.encode('iso-8859-1')): ('ISO-8859-1', 1, 'ä'),
            ('ASCII', b'a'): ('ASCII', 1, 'a'),
        }

        for r, exp in list(tests.items()):
            assert _readUrl(url, fetcher=make_fetcher(r)) == exp

        tests = {
            # (overrideEncoding, parentEncoding, (httpencoding, content)):
            #                        readUrl returns
            # ===== 0. OVERRIDE WINS =====
            # override + parent + http
            ('latin1', 'ascii', ('utf-16', b'')): ('latin1', 0, ''),
            ('latin1', 'ascii', ('utf-16', b'123')): ('latin1', 0, '123'),
            ('latin1', 'ascii', ('utf-16', 'ä'.encode('iso-8859-1'))): (
                'latin1',
                0,
                'ä',
            ),
            ('latin1', 'ascii', ('utf-16', b'a')): ('latin1', 0, 'a'),
            # + @charset
            ('latin1', 'ascii', ('utf-16', b'@charset "ascii";')): (
                'latin1',
                0,
                '@charset "latin1";',
            ),
            ('latin1', 'ascii', ('utf-16', '@charset "utf-8";ä'.encode('latin1'))): (
                'latin1',
                0,
                '@charset "latin1";ä',
            ),
            ('latin1', 'ascii', ('utf-16', '@charset "utf-8";ä'.encode())): (
                'latin1',
                0,
                '@charset "latin1";\xc3\xa4',
            ),  # read as latin1!
            # override only
            ('latin1', None, None): (None, None, None),
            ('latin1', None, (None, b'')): ('latin1', 0, ''),
            ('latin1', None, (None, b'123')): ('latin1', 0, '123'),
            ('latin1', None, (None, 'ä'.encode('iso-8859-1'))): ('latin1', 0, 'ä'),
            ('latin1', None, (None, b'a')): ('latin1', 0, 'a'),
            # + @charset
            ('latin1', None, (None, b'@charset "ascii";')): (
                'latin1',
                0,
                '@charset "latin1";',
            ),
            ('latin1', None, (None, '@charset "utf-8";ä'.encode('latin1'))): (
                'latin1',
                0,
                '@charset "latin1";ä',
            ),
            ('latin1', None, (None, '@charset "utf-8";ä'.encode())): (
                'latin1',
                0,
                '@charset "latin1";\xc3\xa4',
            ),  # read as latin1!
            # override + parent
            ('latin1', 'ascii', None): (None, None, None),
            ('latin1', 'ascii', (None, b'')): ('latin1', 0, ''),
            ('latin1', 'ascii', (None, b'123')): ('latin1', 0, '123'),
            ('latin1', 'ascii', (None, 'ä'.encode('iso-8859-1'))): ('latin1', 0, 'ä'),
            ('latin1', 'ascii', (None, b'a')): ('latin1', 0, 'a'),
            # + @charset
            ('latin1', 'ascii', (None, b'@charset "ascii";')): (
                'latin1',
                0,
                '@charset "latin1";',
            ),
            ('latin1', 'ascii', (None, '@charset "utf-8";ä'.encode('latin1'))): (
                'latin1',
                0,
                '@charset "latin1";ä',
            ),
            ('latin1', 'ascii', (None, '@charset "utf-8";ä'.encode())): (
                'latin1',
                0,
                '@charset "latin1";\xc3\xa4',
            ),  # read as latin1!
            # override + http
            ('latin1', None, ('utf-16', b'')): ('latin1', 0, ''),
            ('latin1', None, ('utf-16', b'123')): ('latin1', 0, '123'),
            ('latin1', None, ('utf-16', 'ä'.encode('iso-8859-1'))): ('latin1', 0, 'ä'),
            ('latin1', None, ('utf-16', b'a')): ('latin1', 0, 'a'),
            # + @charset
            ('latin1', None, ('utf-16', b'@charset "ascii";')): (
                'latin1',
                0,
                '@charset "latin1";',
            ),
            ('latin1', None, ('utf-16', '@charset "utf-8";ä'.encode('latin1'))): (
                'latin1',
                0,
                '@charset "latin1";ä',
            ),
            ('latin1', None, ('utf-16', '@charset "utf-8";ä'.encode())): (
                'latin1',
                0,
                '@charset "latin1";\xc3\xa4',
            ),  # read as latin1!
            # ===== 1. HTTP WINS =====
            (None, 'ascii', ('latin1', b'')): ('latin1', 1, ''),
            (None, 'ascii', ('latin1', b'123')): ('latin1', 1, '123'),
            (None, 'ascii', ('latin1', 'ä'.encode('iso-8859-1'))): ('latin1', 1, 'ä'),
            (None, 'ascii', ('latin1', b'a')): ('latin1', 1, 'a'),
            # + @charset
            (None, 'ascii', ('latin1', b'@charset "ascii";')): (
                'latin1',
                1,
                '@charset "latin1";',
            ),
            (None, 'ascii', ('latin1', '@charset "utf-8";ä'.encode('latin1'))): (
                'latin1',
                1,
                '@charset "latin1";ä',
            ),
            (None, 'ascii', ('latin1', '@charset "utf-8";ä'.encode())): (
                'latin1',
                1,
                '@charset "latin1";\xc3\xa4',
            ),  # read as latin1!
            # ===== 2. @charset WINS =====
            (None, 'ascii', (None, b'@charset "latin1";')): (
                'latin1',
                2,
                '@charset "latin1";',
            ),
            (None, 'ascii', (None, '@charset "latin1";ä'.encode('latin1'))): (
                'latin1',
                2,
                '@charset "latin1";ä',
            ),
            (None, 'ascii', (None, '@charset "latin1";ä'.encode())): (
                'latin1',
                2,
                '@charset "latin1";\xc3\xa4',
            ),  # read as latin1!
            # ===== 2. BOM WINS =====
            (None, 'ascii', (None, 'ä'.encode('utf-8-sig'))): (
                'utf-8-sig',
                2,
                '\xe4',
            ),  # read as latin1!
            (None, 'ascii', (None, '@charset "utf-8";ä'.encode('utf-8-sig'))): (
                'utf-8-sig',
                2,
                '@charset "utf-8";\xe4',
            ),  # read as latin1!
            (None, 'ascii', (None, '@charset "latin1";ä'.encode('utf-8-sig'))): (
                'utf-8-sig',
                2,
                '@charset "utf-8";\xe4',
            ),  # read as latin1!
            # ===== 4. parentEncoding WINS =====
            (None, 'latin1', (None, b'')): ('latin1', 4, ''),
            (None, 'latin1', (None, b'123')): ('latin1', 4, '123'),
            (None, 'latin1', (None, 'ä'.encode('iso-8859-1'))): ('latin1', 4, 'ä'),
            (None, 'latin1', (None, b'a')): ('latin1', 4, 'a'),
            (None, 'latin1', (None, 'ä'.encode())): (
                'latin1',
                4,
                '\xc3\xa4',
            ),  # read as latin1!
            # ===== 5. default WINS which in this case is None! =====
            (None, None, (None, b'')): ('utf-8', 5, ''),
            (None, None, (None, b'123')): ('utf-8', 5, '123'),
            (None, None, (None, b'a')): ('utf-8', 5, 'a'),
            (None, None, (None, 'ä'.encode())): (
                'utf-8',
                5,
                'ä',
            ),  # read as utf-8
            (
                None,
                None,
                (None, 'ä'.encode('iso-8859-1')),
            ): (  # trigger UnicodeDecodeError!
                'utf-8',
                5,
                None,
            ),
        }
        for (override, parent, r), exp in list(tests.items()):
            assert (
                _readUrl(
                    url,
                    overrideEncoding=override,
                    parentEncoding=parent,
                    fetcher=make_fetcher(r),
                )
                == exp
            )

    def test_defaultFetcher(self):  # noqa: C901
        """util._defaultFetcher"""

        class Response:
            """urllib2.Reponse mock"""

            def __init__(self, url, contenttype, content, exception=None, args=None):
                self.url = url

                m = Message()
                m['content-type'] = contenttype

                self.mimetype = m.get_content_type()
                self.charset = m.get_param('charset', None)

                self.text = content

                self.exception = exception
                self.args = args

            def geturl(self):
                return self.url

            def info(self):
                mimetype, charset = self.mimetype, self.charset

                class Info:
                    # py2x
                    def gettype(self):
                        return mimetype

                    def getparam(self, name=None):
                        return charset

                    # py 3x
                    get_content_type = gettype
                    get_content_charset = getparam  # here always charset!

                return Info()

            def read(self):
                # returns fake text or raises fake exception
                if not self.exception:
                    return self.text
                else:
                    raise self.exception(*self.args)

        def urlopen(url, contenttype=None, content=None, exception=None, args=None):
            # return an mock which returns parameterized Response
            def x(*ignored):
                if exception:
                    raise exception(*args)
                else:
                    return Response(
                        url, contenttype, content, exception=exception, args=args
                    )

            return x

        urlopenpatch = 'urllib.request.urlopen'

        # positive tests
        tests = {
            # content-type, contentstr: encoding, contentstr
            ('text/css', '€'.encode()): (None, '€'.encode()),
            ('text/css;charset=utf-8', '€'.encode()): (
                'utf-8',
                '€'.encode(),
            ),
            ('text/css;charset=ascii', 'a'): ('ascii', 'a'),
        }
        url = 'http://example.com/test.css'
        for (contenttype, content), exp in list(tests.items()):

            @mock.patch(urlopenpatch, new=urlopen(url, contenttype, content))
            def do(url):
                return _defaultFetcher(url)

            assert exp == do(url)

        # wrong mimetype
        @mock.patch(urlopenpatch, new=urlopen(url, 'text/html', 'a'))
        def do(url):
            return _defaultFetcher(url)

        with pytest.raises(ValueError):
            do(url)

        # calling url results in fake exception

        # py2 ~= py3 raises error earlier than urlopen!
        tests = {
            '1': (ValueError, ['invalid value for url']),
            # _readUrl('mailto:a.css')
            'mailto:e4': (urllib.error.URLError, ['urlerror']),
            # cannot resolve x, IOError
            'http://x': (urllib.error.URLError, ['ioerror']),
        }
        for url, (exception, args) in list(tests.items()):

            @mock.patch(urlopenpatch, new=urlopen(url, exception=exception, args=args))
            def do(url):
                return _defaultFetcher(url)

            with pytest.raises(exception):
                do(url)

        urlrequestpatch = 'urllib.request.Request'
        tests = {
            # _readUrl('http://cthedot.de/__UNKNOWN__.css')
            'e2': (urllib.error.HTTPError, ['u', 500, 'server error', {}, None]),
            'e3': (urllib.error.HTTPError, ['u', 404, 'not found', {}, None]),
        }
        for url, (exception, args) in list(tests.items()):

            @mock.patch(
                urlrequestpatch, new=urlopen(url, exception=exception, args=args)
            )
            def do(url):
                return _defaultFetcher(url)

            with pytest.raises(exception):
                do(url)


class TestLazyRegex:
    """Tests for cssutils.util.LazyRegex."""

    def setup_method(self):
        self.lazyre = LazyRegex('f.o')

    def test_public_interface(self):
        methods = [
            'search',
            'match',
            'split',
            'sub',
            'subn',
            'findall',
            'finditer',
            'pattern',
            'flags',
            'groups',
            'groupindex',
        ]
        for method in methods:
            assert hasattr(self.lazyre, method), 'expected %r public attribute' % method

    def test_ensure(self):
        assert self.lazyre.matcher is None
        self.lazyre.ensure()
        assert self.lazyre.matcher is not None

    def test_calling(self):
        assert self.lazyre('bar') is None
        match = self.lazyre('foobar')
        assert match.group() == 'foo'

    def test_matching(self):
        assert self.lazyre.match('bar') is None
        match = self.lazyre.match('foobar')
        assert match.group() == 'foo'

    def test_matching_with_position_parameters(self):
        assert self.lazyre.match('foo', 1) is None
        assert self.lazyre.match('foo', 0, 2) is None

    def test_searching(self):
        assert self.lazyre.search('rafuubar') is None
        match = self.lazyre.search('rafoobar')
        assert match.group() == 'foo'

    def test_searching_with_position_parameters(self):
        assert self.lazyre.search('rafoobar', 3) is None
        assert self.lazyre.search('rafoobar', 0, 4) is None
        match = self.lazyre.search('rafoofuobar', 4)
        assert match.group() == 'fuo'

    def test_split(self):
        assert self.lazyre.split('rafoobarfoobaz') == ['ra', 'bar', 'baz']
        assert self.lazyre.split('rafoobarfoobaz', 1) == ['ra', 'barfoobaz']

    def test_findall(self):
        assert self.lazyre.findall('rafoobarfuobaz') == ['foo', 'fuo']

    def test_finditer(self):
        result = self.lazyre.finditer('rafoobarfuobaz')
        assert [m.group() for m in result] == ['foo', 'fuo']

    def test_sub(self):
        assert self.lazyre.sub('bar', 'foofoo') == 'barbar'
        assert self.lazyre.sub(lambda x: 'baz', 'foofoo') == 'bazbaz'

    def test_subn(self):
        subbed = self.lazyre.subn('bar', 'foofoo')
        assert subbed == ('barbar', 2)
        subbed = self.lazyre.subn(lambda x: 'baz', 'foofoo')
        assert subbed == ('bazbaz', 2)

    def test_groups(self):
        lazyre = LazyRegex('(.)(.)')
        assert lazyre.groups is None
        lazyre.ensure()
        assert lazyre.groups == 2

    def test_groupindex(self):
        lazyre = LazyRegex('(?P<foo>.)')
        assert lazyre.groupindex is None
        lazyre.ensure()
        assert lazyre.groupindex == {'foo': 1}

    def test_flags(self):
        self.lazyre.ensure()
        assert self.lazyre.flags == re.compile('.').flags

    def test_pattern(self):
        assert self.lazyre.pattern == 'f.o'
