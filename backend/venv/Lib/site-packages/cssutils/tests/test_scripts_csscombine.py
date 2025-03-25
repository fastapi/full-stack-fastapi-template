"""Testcases for cssutils.scripts.csscombine"""

import cssutils
from cssutils.script import csscombine

from . import basetest


class TestCSSCombine:
    C = '@namespace s2"uri";s2|sheet-1{top:1px}s2|sheet-2{top:2px}proxy{top:3px}'

    def test_combine(self):
        "scripts.csscombine()"

        # path, SHOULD be keyword argument!
        csspath = basetest.get_sheet_filename('csscombine-proxy.css')
        combined = csscombine(csspath)
        assert combined == self.C.encode()
        combined = csscombine(path=csspath, targetencoding='ascii')
        assert combined == ('@charset "ascii";' + self.C).encode()

        # url
        cssurl = cssutils.helper.path2url(csspath)
        combined = csscombine(url=cssurl)
        assert combined == self.C.encode()
        combined = csscombine(url=cssurl, targetencoding='ascii')
        assert combined == ('@charset "ascii";' + self.C).encode()

        # cssText
        # TODO: really need binary or can handle str too?
        f = open(csspath, mode="rb")
        cssText = f.read()
        f.close()
        combined = csscombine(cssText=cssText, href=cssurl)
        assert combined == self.C.encode()
        combined = csscombine(cssText=cssText, href=cssurl, targetencoding='ascii')
        assert combined == ('@charset "ascii";' + self.C).encode()

    def test_combine_resolveVariables(self):
        "scripts.csscombine(minify=..., resolveVariables=...)"
        # no actual imports but checking if minify and resolveVariables work
        cssText = '''
        @variables {
            c: #0f0;
        }
        a {
            color: var(c);
        }
        '''
        # default minify
        assert (
            csscombine(cssText=cssText, resolveVariables=False)
            == b'@variables{c:#0f0}a{color:var(c)}'
        )
        assert csscombine(cssText=cssText) == b'a{color:#0f0}'

        # no minify
        assert (
            csscombine(cssText=cssText, minify=False, resolveVariables=False)
            == b'@variables {\n    c: #0f0\n    }\na {\n    color: var(c)\n    }'
        )
        assert (
            csscombine(cssText=cssText, minify=False) == b'a {\n    color: #0f0\n    }'
        )
