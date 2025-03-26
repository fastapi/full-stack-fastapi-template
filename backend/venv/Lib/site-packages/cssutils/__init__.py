"""
CSS Cascading Style Sheets library for Python

A Python package to parse and build CSS Cascading Style Sheets. DOM only, not
any rendering facilities!

Based upon and partly implementing the following specifications :

`CSS 2.1 <http://www.w3.org/TR/CSS2/>`__
    General CSS rules and properties are defined here
`CSS 2.1 Errata
    <http://www.w3.org/Style/css2-updates/CR-CSS21-20070719-errata.html>`__
    A few errata, mainly the definition of CHARSET_SYM tokens
`CSS3 Module: Syntax <http://www.w3.org/TR/css3-syntax/>`__
    Used in parts since cssutils 0.9.4. cssutils tries to use the features from
    CSS 2.1 and CSS 3 with preference to CSS3 but as this is not final yet some
    parts are from CSS 2.1
`MediaQueries <http://www.w3.org/TR/css3-mediaqueries/>`__
    MediaQueries are part of ``stylesheets.MediaList`` since v0.9.4, used in
    @import and @media rules.
`Namespaces <http://dev.w3.org/csswg/css3-namespace/>`__
    Added in v0.9.1, updated to definition in CSSOM in v0.9.4, updated in 0.9.5
    for dev version
`CSS3 Module: Pages Media <http://www.w3.org/TR/css3-page/>`__
    Most properties of this spec are implemented including MarginRules
`Selectors <http://www.w3.org/TR/css3-selectors/>`__
    The selector syntax defined here (and not in CSS 2.1) should be parsable
    with cssutils (*should* mind though ;) )

`DOM Level 2 Style CSS <http://www.w3.org/TR/DOM-Level-2-Style/css.html>`__
    DOM for package css. 0.9.8 removes support for CSSValue and related API,
    see PropertyValue and Value API for now
`DOM Level 2 Style Stylesheets
    <http://www.w3.org/TR/DOM-Level-2-Style/stylesheets.html>`__
    DOM for package stylesheets
`CSSOM <http://dev.w3.org/csswg/cssom/>`__
    A few details (mainly the NamespaceRule DOM) is taken from here. Plan is
    to move implementation to the stuff defined here which is newer but still
    no REC so might change anytime...


The cssutils tokenizer is a customized implementation of `CSS3 Module: Syntax
(W3C Working Draft 13 August 2003) <http://www.w3.org/TR/css3-syntax/>`__ which
itself is based on the CSS 2.1 tokenizer. It tries to be as compliant as
possible but uses some (helpful) parts of the CSS 2.1 tokenizer.

I guess cssutils is neither CSS 2.1 nor CSS 3 compliant but tries to at least
be able to parse both grammars including some more real world cases (some CSS
hacks are actually parsed and serialized). Both official grammars are not final
nor bugfree but still feasible. cssutils aim is not to be fully compliant to
any CSS specification (the specifications seem to be in a constant flow anyway)
but cssutils *should* be able to read and write as many as possible CSS
stylesheets "in the wild" while at the same time implement the official APIs
which are well documented. Some minor extensions are provided as well.

Please visit https://cssutils.readthedocs.io/ for more details.

Example::

    >>> from cssutils import CSSParser
    >>> parser = CSSParser()
    >>> sheet = parser.parseString('a { color: red}')

    # TODO: shouldn't have to decode here
    >>> print(sheet.cssText.decode())
    a {
        color: red
        }

"""

import functools
import itertools
import os.path
import urllib.parse
import urllib.request
import xml.dom

from . import css, errorhandler, stylesheets
from .parse import CSSParser
from .profiles import Profiles
from .serialize import CSSSerializer

__all__ = ['css', 'stylesheets', 'CSSParser', 'CSSSerializer']

log = errorhandler.ErrorHandler()
ser = CSSSerializer()
profile = Profiles(log=log)

# used by Selector defining namespace prefix '*'
_ANYNS = -1


class DOMImplementationCSS:
    """This interface allows the DOM user to create a CSSStyleSheet
    outside the context of a document. There is no way to associate
    the new CSSStyleSheet with a document in DOM Level 2.

    This class is its *own factory*, as it is given to
    xml.dom.registerDOMImplementation which simply calls it and receives
    an instance of this class then.
    """

    _features = [
        ('css', '1.0'),
        ('css', '2.0'),
        ('stylesheets', '1.0'),
        ('stylesheets', '2.0'),
    ]

    def createCSSStyleSheet(self, title, media):
        """
        Creates a new CSSStyleSheet.

        title of type DOMString
            The advisory title. See also the Style Sheet Interfaces
            section.
        media of type DOMString
            The comma-separated list of media associated with the new style
            sheet. See also the Style Sheet Interfaces section.

        returns
            CSSStyleSheet: A new CSS style sheet.

        TODO: DOMException
            SYNTAX_ERR: Raised if the specified media string value has a
            syntax error and is unparsable.
        """
        import warnings

        warning = (
            "Deprecated, see "
            "https://web.archive.org/web/20200701035537/"
            "https://bitbucket.org/cthedot/cssutils/issues/69#comment-30669799"
        )
        warnings.warn(warning, DeprecationWarning, stacklevel=2)
        return css.CSSStyleSheet(title=title, media=media)

    def createDocument(self, *args, **kwargs):
        # sometimes cssutils is picked automatically for
        # xml.dom.getDOMImplementation, so provide an implementation
        # see (https://web.archive.org/web/20200701035537/
        # https://bitbucket.org/cthedot/cssutils/issues/69)
        import xml.dom.minidom as minidom

        return minidom.DOMImplementation().createDocument(*args, **kwargs)

    def createDocumentType(self, *args, **kwargs):
        # sometimes cssutils is picked automatically for
        # xml.dom.getDOMImplementation, so provide an implementation
        # see (https://web.archive.org/web/20200701035537/
        # https://bitbucket.org/cthedot/cssutils/issues/69)
        import xml.dom.minidom as minidom

        return minidom.DOMImplementation().createDocumentType(*args, **kwargs)

    def hasFeature(self, feature, version):
        return (feature.lower(), str(version)) in self._features


xml.dom.registerDOMImplementation('cssutils', DOMImplementationCSS)


def _parser_redirect(name):
    def func(*args, **kwargs):
        return getattr(CSSParser(), name)(*args, **kwargs)

    func.__doc__ = getattr(CSSParser, name).__doc__
    func.__qualname__ = func.__name__ = name
    return func


parseString = _parser_redirect('parseString')
parseFile = _parser_redirect('parseFile')
parseUrl = _parser_redirect('parseUrl')
parseStyle = _parser_redirect('parseStyle')


def setSerializer(serializer):
    """Set the global serializer used by all class in cssutils."""
    globals().update(ser=serializer)


def _style_declarations(base):
    """
    Recursively find all CSSStyleDeclarations.
    """
    for rule in getattr(base, 'cssRules', ()):
        yield from _style_declarations(rule)
    if hasattr(base, 'style'):
        yield base.style


def getUrls(sheet):
    """Retrieve all ``url(urlstring)`` values (in e.g.
    :class:`cssutils.css.CSSImportRule` or ``cssutils.css.CSSValue``
    objects of given `sheet`.

    :param sheet:
        :class:`cssutils.css.CSSStyleSheet` object whose URLs are yielded

    This function is a generator. The generated URL values exclude ``url(`` and
    ``)`` and surrounding single or double quotes.
    """
    imports = (rule.href for rule in sheet if rule.type == rule.IMPORT_RULE)

    other = (
        value.uri
        for style in _style_declarations(sheet)
        for value in _uri_values(style)
    )

    return itertools.chain(imports, other)


def _uri_values(style):
    return (
        value
        for prop in style.getProperties(all=True)
        for value in prop.propertyValue
        if value.type == 'URI'
    )


_flatten = itertools.chain.from_iterable


@functools.singledispatch
def replaceUrls(sheet, replacer, ignoreImportRules=False):
    """Replace all URLs in :class:`cssutils.css.CSSImportRule` or
    ``cssutils.css.CSSValue`` objects of given `sheet`.

    :param sheet:
        a :class:`cssutils.css.CSSStyleSheet` to be modified in place.
    :param replacer:
        a function which is called with a single argument `url` which
        is the current value of each url() excluding ``url(``, ``)`` and
        surrounding (single or double) quotes.
    :param ignoreImportRules:
        if ``True`` does not call `replacer` with URLs from @import rules.
    """
    imports = (
        rule
        for rule in sheet
        if rule.type == rule.IMPORT_RULE and not ignoreImportRules
    )
    for rule in imports:
        rule.href = replacer(rule.href)

    for value in _flatten(map(_uri_values, _style_declarations(sheet))):
        value.uri = replacer(value.uri)


@replaceUrls.register(css.CSSStyleDeclaration)
def _(style, replacer, ignoreImportRules=False):
    """Replace all URLs in :class:`cssutils.css.CSSImportRule` or
    :class:`cssutils.css.CSSValue` objects of given `style`.

    :param style:
        a :class:`cssutils.css.CSSStyleDeclaration` to be modified in place.
    :param replacer:
        a function which is called with a single argument `url` which
        is the current value of each url() excluding ``url(``, ``)`` and
        surrounding (single or double) quotes.
    :param ignoreImportRules:
        not applicable, ignored.
    """
    for value in _uri_values(style):
        value.uri = replacer(value.uri)


class Replacer:
    """
    A replacer that uses base to return adjusted URLs.
    """

    def __init__(self, base):
        self.base = self.extract_base(base)

    def __call__(self, uri):
        scheme, location, path, query, fragment = urllib.parse.urlsplit(uri)
        if scheme or location or path.startswith('/'):
            # keep anything absolute
            return uri

        path, filename = os.path.split(path)
        combined = os.path.normpath(os.path.join(self.base, path, filename))
        return urllib.request.pathname2url(combined)

    @staticmethod
    def extract_base(uri):
        _, _, raw_path, _, _ = urllib.parse.urlsplit(uri)
        base_path, _ = os.path.split(raw_path)
        return base_path


def resolveImports(sheet, target=None):
    """
    Recursively combine all rules in given `sheet` into a `target` sheet.
    Attempts to wrap @import rules that use media information into
    @media rules, keeping the media information. This approach may not work in
    all instances (e.g. if an @import rule itself contains an @import rule
    with different media infos or if it contains rules that may not be
    used inside an @media block like @namespace rules). In these cases,
    the @import rule from the original sheet takes precedence and a WARNING
    is issued.

    :param sheet:
        :class:`cssutils.css.CSSStyleSheet` from which all import rules are
        resolved and added to a resulting *flat* sheet.
    :param target:
        A :class:`cssutils.css.CSSStyleSheet` object that will be the
        resulting *flat* sheet if given.
    :returns:
        :class:`cssutils.css.CSSStyleSheet` with imports resolved.
    """
    if not target:
        target = css.CSSStyleSheet(
            href=sheet.href, media=sheet.media, title=sheet.title
        )

    for rule in sheet.cssRules:
        if rule.type == rule.CHARSET_RULE:
            pass
        elif rule.type == rule.IMPORT_RULE:
            _resolve_import(rule, target)
        else:
            target.add(rule)

    return target


class MediaCombineDisallowed(Exception):
    @classmethod
    def check(cls, sheet):
        """
        Check if rules present that may not be combined with media.
        """
        failed = list(itertools.filterfalse(cls._combinable, sheet))
        if failed:
            raise cls(failed)

    @property
    def failed(self):
        return self.args[0]

    def _combinable(rule):
        combinable = rule.COMMENT, rule.STYLE_RULE, rule.IMPORT_RULE
        return rule.type in combinable


def _resolve_import(rule, target):
    log.info('Processing @import %r' % rule.href, neverraise=True)

    if not rule.hrefFound:
        # keep @import as it is
        log.error(
            'Cannot get referenced stylesheet %r, keeping rule' % rule.href,
            neverraise=True,
        )
        target.add(rule)
        return

    # add all rules of @import to current sheet
    target.add(css.CSSComment(cssText='/* START @import "%s" */' % rule.href))

    try:
        # nested imports
        importedSheet = resolveImports(rule.styleSheet)
    except xml.dom.HierarchyRequestErr as e:
        log.warn(
            '@import: Cannot resolve target, keeping rule: %s' % e,
            neverraise=True,
        )
        target.add(rule)
        return

    # adjust relative URI references
    log.info('@import: Adjusting paths for %r' % rule.href, neverraise=True)
    replaceUrls(importedSheet, Replacer(rule.href), ignoreImportRules=True)

    try:
        media_proxy = _check_media_proxy(rule, importedSheet)
    except MediaCombineDisallowed as exc:
        log.warn(
            'Cannot combine imported sheet with given media as rules other than '
            f'comments or stylerules; found {exc.failed[0]!r}, keeping {rule.cssText}',
            neverraise=True,
        )
        target.add(rule)
        return

    imp_target = media_proxy or target
    for r in importedSheet:
        imp_target.add(r)

    if media_proxy:
        target.add(media_proxy)


def _check_media_proxy(rule, importedSheet):
    # might have to wrap rules in @media if media given
    if rule.media.mediaText == 'all':
        return

    MediaCombineDisallowed.check(importedSheet)

    # wrap in @media if media is not `all`
    log.info(
        '@import: Wrapping some rules in @media '
        f' to keep media: {rule.media.mediaText}',
        neverraise=True,
    )
    return css.CSSMediaRule(rule.media.mediaText)


if __name__ == '__main__':
    print(__doc__)
