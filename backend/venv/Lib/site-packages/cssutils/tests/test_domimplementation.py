"""Testcases for cssutils.css.DOMImplementation"""

import warnings
import xml.dom
import xml.dom.minidom

import pytest

import cssutils


@pytest.fixture
def domimpl():
    return cssutils.DOMImplementationCSS()


class TestDOMImplementation:
    def test_createCSSStyleSheet(self, domimpl):
        "DOMImplementationCSS.createCSSStyleSheet()"
        title, media = 'Test Title', cssutils.stylesheets.MediaList('all')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            sheet = domimpl.createCSSStyleSheet(title, media)
        assert isinstance(sheet, cssutils.css.CSSStyleSheet)
        assert title == sheet.title
        assert media == sheet.media

    def test_createDocument(self, domimpl):
        "DOMImplementationCSS.createDocument()"
        doc = domimpl.createDocument(None, None, None)
        assert isinstance(doc, xml.dom.minidom.Document)

    def test_createDocumentType(self, domimpl):
        "DOMImplementationCSS.createDocumentType()"
        doctype = domimpl.createDocumentType('foo', 'bar', 'raboof')
        assert isinstance(doctype, xml.dom.minidom.DocumentType)

    def test_hasFeature(self, domimpl):
        "DOMImplementationCSS.hasFeature()"
        tests = [
            ('css', '1.0'),
            ('css', '2.0'),
            ('stylesheets', '1.0'),
            ('stylesheets', '2.0'),
        ]
        for name, version in tests:
            assert domimpl.hasFeature(name, version)
