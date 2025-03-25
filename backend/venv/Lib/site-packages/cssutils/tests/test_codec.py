"""Testcases for cssutils.codec"""

import codecs
import io

import pytest

from cssutils import codec

iostream = io.BytesIO


class Queue:
    """
    queue: write bytes at one end, read bytes from the other end
    """

    def __init__(self):
        self._buffer = b""

    def write(self, chars):
        # TODO ???
        if isinstance(chars, str):
            chars = chars.encode()
        elif isinstance(chars, int):
            chars = bytes([chars])

        self._buffer += chars

    def read(self, size=-1):
        if size < 0:
            s = self._buffer
            self._buffer = b""
            return s
        else:
            s = self._buffer[:size]
            self._buffer = self._buffer[size:]
            return s


class TestCodec:
    def test_detectencoding_str(self):
        "codec.detectencoding_str()"
        assert codec.detectencoding_str(b'') == (None, False)
        assert codec.detectencoding_str(b'\xef') == (None, False)
        assert codec.detectencoding_str('\xef\x33'.encode()) == ("utf-8", False)
        assert codec.detectencoding_str('\xc3\xaf3'.encode()) == ("utf-8", False)
        assert codec.detectencoding_str(b'\xef\xbb') == (None, False)
        assert codec.detectencoding_str('\xef\xbb\x33'.encode()) == (
            "utf-8",
            False,
        )
        assert codec.detectencoding_str('\xef\xbb\xbf'.encode("utf-8-sig")) == (
            "utf-8-sig",
            True,
        )
        assert codec.detectencoding_str(b'\xff') == (None, False)
        assert codec.detectencoding_str('\xff\x33'.encode()) == ("utf-8", False)
        assert codec.detectencoding_str(b'\xff\xfe') == (None, False)
        assert codec.detectencoding_str('\xff\xfe\x33'.encode("utf-16")) == (
            "utf-16",
            True,
        )
        assert codec.detectencoding_str(b'\xff\xfe\x00') == (
            None,
            False,
        )
        assert codec.detectencoding_str('\xff\xfe\x00\x33'.encode("utf-16")) == (
            "utf-16",
            True,
        )
        assert codec.detectencoding_str('\xff\xfe\x00\x00'.encode("utf-32")) == (
            "utf-32",
            True,
        )
        assert codec.detectencoding_str(b'\x00') == (None, False)
        assert codec.detectencoding_str(b'\x00\x33') == ("utf-8", False)
        assert codec.detectencoding_str(b'\x00\x00') == (None, False)
        assert codec.detectencoding_str(b'\x00\x00\x33') == ("utf-8", False)
        assert codec.detectencoding_str(b'\x00\x00\xfe') == (
            None,
            False,
        )
        assert codec.detectencoding_str(b'\x00\x00\x00\x33') == ("utf-8", False)
        assert codec.detectencoding_str(b'\x00\x00\x00@') == (
            "utf-32-be",
            False,
        )
        assert codec.detectencoding_str('\x00\x00\xfe\xff'.encode('utf-32')) == (
            "utf-32",
            True,
        )
        assert codec.detectencoding_str(b'@') == (None, False)
        assert codec.detectencoding_str(b'@\x33') == ("utf-8", False)
        assert codec.detectencoding_str(b'@\x00') == (None, False)
        assert codec.detectencoding_str(b'@\x00\x33') == ("utf-8", False)
        assert codec.detectencoding_str(b'@\x00\x00') == (None, False)
        assert codec.detectencoding_str(b'@\x00\x00\x33') == ("utf-8", False)
        assert codec.detectencoding_str(b'@\x00\x00\x00') == (
            "utf-32-le",
            False,
        )
        assert codec.detectencoding_str(b'@c') == (None, False)
        assert codec.detectencoding_str(b'@ch') == (None, False)
        assert codec.detectencoding_str(b'@cha') == (None, False)
        assert codec.detectencoding_str(b'@char') == (None, False)
        assert codec.detectencoding_str(b'@chars') == (None, False)
        assert codec.detectencoding_str(b'@charse') == (None, False)
        assert codec.detectencoding_str(b'@charset') == (None, False)
        assert codec.detectencoding_str(b'@charset ') == (None, False)
        assert codec.detectencoding_str(b'@charset "') == (None, False)
        assert codec.detectencoding_str(b'@charset "x') == (None, False)
        assert codec.detectencoding_str(b'@charset ""') == ("", True)
        assert codec.detectencoding_str(b'@charset "x"') == ("x", True)
        assert codec.detectencoding_str(b"@", False) == (None, False)
        assert codec.detectencoding_str(b"@", True) == ("utf-8", False)
        assert codec.detectencoding_str(b"@c", False) == (None, False)
        assert codec.detectencoding_str(b"@c", True) == ("utf-8", False)

    def test_detectencoding_unicode(self):
        "codec.detectencoding_unicode()"
        # Unicode version (only parses the header)
        assert codec.detectencoding_unicode('@charset "x') == (None, False)
        assert codec.detectencoding_unicode('a {}') == ("utf-8", False)
        assert codec.detectencoding_unicode('@charset "x', True) == (None, False)
        assert codec.detectencoding_unicode('@charset "x"') == ("x", True)

    def test_fixencoding(self):
        "codec._fixencoding()"
        s = '@charset "'
        assert codec._fixencoding(s, "utf-8") is None

        s = '@charset "x'
        assert codec._fixencoding(s, "utf-8") is None

        s = '@charset "x'
        assert codec._fixencoding(s, "utf-8", True) == s

        s = '@charset x'
        assert codec._fixencoding(s, "utf-8") == s

        s = '@charset "x"'
        assert codec._fixencoding(s, "utf-8") == s.replace('"x"', '"utf-8"')

    def test_decoder(self):  # noqa: C901
        "codecs.decoder"

        def checkauto(encoding, input='@charset "x";g\xfcrk\u20ac{}'):
            outputencoding = encoding
            if outputencoding == "utf-8-sig":
                outputencoding = "utf-8"
            # Check stateless decoder with encoding autodetection
            d = codecs.getdecoder("css")
            assert d(input.encode(encoding))[0] == input.replace(
                '"x"', '"%s"' % outputencoding
            )

            # Check stateless decoder with specified encoding
            assert d(input.encode(encoding), encoding=encoding)[0] == input.replace(
                '"x"', '"%s"' % outputencoding
            )

            if hasattr(codec, "getincrementaldecoder"):
                # Check incremental decoder with encoding autodetection
                id = codecs.getincrementaldecoder("css")()
                assert "".join(id.iterdecode(input.encode(encoding))) == input.replace(
                    '"x"', '"%s"' % outputencoding
                )

                # Check incremental decoder with specified encoding
                id = codecs.getincrementaldecoder("css")(encoding=encoding)
                assert "".join(id.iterdecode(input.encode(encoding))) == input.replace(
                    '"x"', '"%s"' % outputencoding
                )

            # Check stream reader with encoding autodetection
            q = Queue()
            sr = codecs.getreader("css")(q)
            result = []
            # TODO: py3 only???
            for c in input.encode(encoding):
                q.write(c)
                result.append(sr.read())
            assert "".join(result) == input.replace('"x"', '"%s"' % outputencoding)

            # Check stream reader with specified encoding
            q = Queue()
            sr = codecs.getreader("css")(q, encoding=encoding)
            result = []
            for c in input.encode(encoding):
                q.write(c)
                result.append(sr.read())
            assert "".join(result) == input.replace('"x"', '"%s"' % outputencoding)

        # Autodetectable encodings
        checkauto("utf-8-sig")
        checkauto("utf-16")
        checkauto("utf-16-le")
        checkauto("utf-16-be")
        checkauto("utf-32")
        checkauto("utf-32-le")
        checkauto("utf-32-be")

        def checkdecl(encoding, input='@charset "%s";g\xfcrk{}'):
            # Check stateless decoder with encoding autodetection
            d = codecs.getdecoder("css")
            input = input % encoding
            outputencoding = encoding
            if outputencoding == "utf-8-sig":
                outputencoding = "utf-8"
            assert d(input.encode(encoding))[0] == input

            # Check stateless decoder with specified encoding
            assert d(input.encode(encoding), encoding=encoding)[0] == input

            if hasattr(codec, "getincrementaldecoder"):
                # Check incremental decoder with encoding autodetection
                id = codecs.getincrementaldecoder("css")()
                assert "".join(id.iterdecode(input.encode(encoding))) == input

                # Check incremental decoder with specified encoding
                id = codecs.getincrementaldecoder("css")(encoding)
                assert "".join(id.iterdecode(input.encode(encoding))) == input

            # Check stream reader with encoding autodetection
            q = Queue()
            sr = codecs.getreader("css")(q)
            result = []
            for c in input.encode(encoding):
                q.write(c)
                result.append(sr.read())
            assert "".join(result) == input

            # Check stream reader with specified encoding
            q = Queue()
            sr = codecs.getreader("css")(q, encoding=encoding)
            result = []
            for c in input.encode(encoding):
                q.write(c)
                result.append(sr.read())
            assert "".join(result) == input

        # Use correct declaration
        checkdecl("utf-8")
        checkdecl("iso-8859-1", '@charset "%s";g\xfcrk')
        checkdecl("iso-8859-15")
        checkdecl("cp1252")

        # No recursion
        with pytest.raises(ValueError):
            b'@charset "css";div{}'.decode("css")

    def test_encoder(self):
        "codec.encoder"

        def check(encoding, input='@charset "x";g\xfcrk\u20ac{}'):
            outputencoding = encoding
            if outputencoding == "utf-8-sig":
                outputencoding = "utf-8"

            # Check stateless encoder with encoding autodetection
            e = codecs.getencoder("css")
            inputdecl = input.replace('"x"', '"%s"' % encoding)
            outputdecl = input.replace('"x"', '"%s"' % outputencoding)
            assert e(inputdecl)[0].decode(encoding) == outputdecl

            # Check stateless encoder with specified encoding
            assert e(input, encoding=encoding)[0].decode(encoding) == outputdecl

            if hasattr(codec, "getincrementalencoder"):
                # Check incremental encoder with encoding autodetection
                ie = codecs.getincrementalencoder("css")()
                assert "".join(ie.iterencode(inputdecl)).decode(encoding) == outputdecl

                # Check incremental encoder with specified encoding
                ie = codecs.getincrementalencoder("css")(encoding=encoding)
                assert "".join(ie.iterencode(input)).decode(encoding) == outputdecl

            # Check stream writer with encoding autodetection
            q = Queue()
            sw = codecs.getwriter("css")(q)
            for c in inputdecl:  # .encode(outputencoding): # TODO: .encode()???
                sw.write(c)
            assert q.read().decode(encoding) == input.replace(
                '"x"', '"%s"' % outputencoding
            )

            # Check stream writer with specified encoding
            q = Queue()
            sw = codecs.getwriter("css")(q, encoding=encoding)
            for c in input:
                sw.write(c)
            assert q.read().decode(encoding) == input.replace(
                '"x"', '"%s"' % outputencoding
            )

        # Autodetectable encodings
        check("utf-8-sig")
        check("utf-16")
        check("utf-16-le")
        check("utf-16-be")
        check("utf-32")
        check("utf-32-le")
        check("utf-32-be")
        check("utf-8")
        check("iso-8859-1", '@charset "x";g\xfcrk{}')
        check("iso-8859-15")
        check("cp1252")

        # No recursion
        with pytest.raises(ValueError):
            '@charset "css";div{}'.encode("css")

    def test_decode_force(self):
        "codec.decode (force)"
        info = codecs.lookup("css")

        def decodeall(input, **kwargs):
            # Py 2.5: info.decode('@charset "utf-8"; x')
            return info[1](input, **kwargs)[0]

        def incdecode(input, **kwargs):
            decoder = info.incrementaldecoder(**kwargs)
            return decoder.decode(input)

        def streamdecode(input, **kwargs):
            stream = iostream(input)  # py3 .decode('utf-8') but still error?!
            reader = info.streamreader(stream, **kwargs)
            return reader.read()

        for d in (decodeall, incdecode, streamdecode):
            # input = '@charset "utf-8"; \xc3\xbf'
            # output = u'@charset "utf-8"; \xff'
            # self.assertEqual(d(input), output)
            #
            # input = '@charset "utf-8"; \xc3\xbf'
            # output = u'@charset "iso-8859-1"; \xc3\xbf'
            # self.assertEqual(d(input, encoding="iso-8859-1", force=True), output)
            #
            # input = '\xc3\xbf'
            # output = u'\xc3\xbf'
            # self.assertEqual(d(input, encoding="iso-8859-1", force=True), output)
            #
            # input = '@charset "utf-8"; \xc3\xbf'
            # output = u'@charset "utf-8"; \xff'
            # self.assertEqual(d(input, encoding="iso-8859-1", force=False), output)

            input = '@charset "utf-8"; \xff'.encode()
            output = '@charset "utf-8"; \xff'
            assert d(input) == output

            # input = b'@charset "utf-8"; \xc3\xbf'
            input = '@charset "utf-8"; \xff'.encode()
            output = '@charset "iso-8859-1"; \xc3\xbf'
            assert d(input, encoding="iso-8859-1", force=True) == output

            # input = b'\xc3\xbf'
            input = '\xff'.encode()
            output = '\xc3\xbf'
            assert d(input, encoding="iso-8859-1", force=True) == output

            # input = b'@charset "utf-8"; \xc3\xbf'
            input = '@charset "utf-8"; \xff'.encode()
            output = '@charset "utf-8"; \xff'
            assert d(input, encoding="iso-8859-1", force=False) == output
