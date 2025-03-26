# encoding: utf-8
from __future__ import unicode_literals

import functools
import logging
import posixpath
import re
import warnings

from cssutils import CSSParser
from lxml import etree
from premailer import Premailer
from premailer.premailer import ExternalNotFoundError

from .compat import urlparse, to_unicode, is_callable
from .loader.local_store import FileNotFound
from .store import MemoryFileStore, LazyHTTPFile
from .template.base import BaseTemplate


class LocalPremailer(Premailer):

    def __init__(self, html, local_loader=None, attribute_name=None, **kw):
        if 'preserve_internal_links' not in kw:
            kw['preserve_internal_links'] = True
        self.local_loader = local_loader
        if attribute_name:
            self.attribute_name = attribute_name
        super(LocalPremailer, self).__init__(html=html, **kw)

    def _load_external(self, url):
        """
        loads an external stylesheet from a remote url or local store
        """
        if url.startswith('//'):
            # then we have to rely on the base_url
            if self.base_url and 'https://' in self.base_url:
                url = 'https:' + url
            else:
                url = 'http:' + url

        if url.startswith('http://') or url.startswith('https://'):
            content = self._load_external_url(url)
        else:
            content = None

            if self.local_loader:
                try:
                    content = self.local_loader[url]
                except FileNotFound:
                    content = None

            if content is None:
                if self.base_url:
                    return self._load_external(urlparse.urljoin(self.base_url, url))
                else:
                    raise ExternalNotFoundError(url)

        return content


class HTMLParser(object):
    _cdata_regex = re.compile(r'\<\!\[CDATA\[(.*?)\]\]\>', re.DOTALL)
    _xml_title_regex = re.compile(r'\<title(.*?)\/\>', re.IGNORECASE)
    default_parser_method = "html"
    default_output_method = "xml"

    def __init__(self, html, method=None, output_method=None):

        self._method = method or self.default_parser_method
        self._output_method = output_method or self.default_output_method

        if self._output_method == 'xml':
            self._html = html.replace('\r\n', '\n')
        else:
            self._html = html

        self._tree = None

    @property
    def html(self):
        return self._html

    @property
    def tree(self):
        if self._tree is None:
            html_data = self._html.strip()
            if self._method == 'xml':
                parser = etree.XMLParser(ns_clean=False, resolve_entities=False)
                self._tree = etree.fromstring(html_data, parser)
            elif self._method == 'html5':
                import html5lib
                parsed = html5lib.parse(html_data, treebuilder='lxml', namespaceHTMLElements=False)
                self._tree = parsed.getroot()
            else:
                parser = etree.HTMLParser()
                self._tree = etree.fromstring(html_data, parser)
        return self._tree

    def to_string(self, encoding='utf-8', **kwargs):
        if self.tree is None:
            return ""
        method = self._output_method
        out = etree.tostring(self.tree, encoding=encoding, method=method, **kwargs).decode(encoding)
        if method == 'xml':
            out = self._cdata_regex.sub(
                lambda m: '/*<![CDATA[*/%s/*]]>*/' % m.group(1),
                out
            )
            # Remove empty "<title/>" which breaks html rendering (Fixes #43)
            out = self._xml_title_regex.sub('', out)
        return out

    def apply_to_images(self, func, images=True, backgrounds=True, styles_uri=True):

        def _apply_to_style_uri(style_text, func):
            dirty = False
            parser = CSSParser().parseStyle(style_text)
            for prop in parser.getProperties(all=True):
                for value in prop.propertyValue:
                    if value.type == 'URI':
                        old_uri = value.uri
                        new_uri = func(old_uri, element=value)
                        if new_uri != old_uri:
                            dirty = True
                            value.uri = new_uri
            if dirty:
                return to_unicode(parser.cssText, 'utf-8')
            else:
                return style_text

        if images:
            # Apply to images from IMG tag
            for img in self.tree.xpath(".//img"):
                if 'src' in img.attrib:
                    img.attrib['src'] = func(img.attrib['src'], element=img)

        if backgrounds:
            # Apply to images from <tag background="X">
            for item in self.tree.xpath("//@background"):
                tag = item.getparent()
                tag.attrib['background'] = func(tag.attrib['background'], element=tag)

        if styles_uri:
            # Apply to style uri
            for item in self.tree.xpath("//@style"):
                tag = item.getparent()
                tag.attrib['style'] = _apply_to_style_uri(tag.attrib['style'], func=func)

    def apply_to_links(self, func):
        # Apply to images from IMG tag
        for a in self.tree.xpath(".//a"):
            if 'href' in a.attrib:
                a.attrib['href'] = func(a.attrib['href'], element=a)

    def add_content_type_meta(self, content_type="text/html", charset="utf-8", element_cls=etree.Element):

        def _get_content_type_meta(head):
            content_type_meta = None
            for meta in head.find('meta') or []:
                http_equiv = meta.get('http-equiv', None)
                if http_equiv and (http_equiv.lower() == 'content_type'):
                    content_type_meta = meta
                    break
            if content_type_meta is None:
                content_type_meta = element_cls('meta')
                head.append(content_type_meta)
            return content_type_meta

        head = self.tree.find('head')
        if head is None:
            # After Premailer.transform there are always HEAD tag
            logging.warning('HEAD not found. This should not happen. Skip.')
            return

        meta = _get_content_type_meta(head)
        meta.set('content', '%s; charset=%s' % (content_type, charset))
        meta.set('http-equiv', "Content-Type")

    def save(self, **kwargs):
        self._html = self.to_string(**kwargs)


class BaseTransformer(HTMLParser):

    UNSAFE_TAGS = ['script', 'object', 'iframe', 'frame', 'base', 'meta', 'link', 'style']

    attachment_store_cls = MemoryFileStore
    attachment_file_cls = LazyHTTPFile
    html_attribute_name = 'data-emails'

    def __init__(self, html, local_loader=None,
                 attachment_store=None,
                 requests_params=None, method=None, base_url=None):

        HTMLParser.__init__(self, html=html, method=method)

        self.attachment_store = attachment_store if attachment_store is not None else self.attachment_store_cls()
        self.local_loader = local_loader
        if base_url and not base_url.endswith('/'):
            base_url = base_url + '/'
        self.base_url = base_url
        self.requests_params = requests_params

        self._premailer = None

    def get_absolute_url(self, url):

        if not self.base_url:
            return url

        if url.startswith('//'):
            if 'https://' in self.base_url:
                url = 'https:' + url
            else:
                url = 'http:' + url
            return url

        if not (url.startswith('http://') or url.startswith('https://')):
            url = urlparse.urljoin(self.base_url, posixpath.normpath(url))

        return url

    def attribute_value(self, el):
        return el is not None \
               and hasattr(el, 'attrib') \
               and el.attrib.get(self.html_attribute_name) \
               or None

    _attribute_value = attribute_value  # deprecated

    def _default_attachment_check(self, el, hints):
        if hints['attrib'] == 'ignore':
            return False
        else:
            return True

    def _load_attachment_func(self, uri, element=None, callback=None, **kw):

        #
        # Load uri from remote url or from local_store
        # Return local uri
        #

        if callback is None:
            # Default callback: skip images with data-emails="ignore" attribute
            callback = lambda _, hints: hints['attrib'] != 'ignore'

        attribute_value = self.attribute_value(element) or ''

        # If callback returns False, skip attachment loading
        if not callback(element, hints={'attrib': attribute_value}):
            return uri

        attachment = self.attachment_store.by_uri(uri)
        if attachment is None:
            attachment = self.attachment_file_cls(
                uri=uri,
                absolute_url=self.get_absolute_url(uri),
                local_loader=self.local_loader,
                content_disposition='inline' if 'inline' in attribute_value else None,
                requests_args=self.requests_params)
            self.attachment_store.add(attachment)
        return attachment.filename

    def get_premailer(self, **kw):
        kw.setdefault('attribute_name', self.html_attribute_name)
        kw.setdefault('method', self._method)
        kw.setdefault('base_url', self.base_url)
        kw.setdefault('local_loader', self.local_loader)
        return LocalPremailer(html=self.tree, **kw)

    @property
    def premailer(self):
        if self._premailer is None:
            self._premailer = self.get_premailer()
        return self._premailer

    def remove_unsafe_tags(self):
        for tag in self.UNSAFE_TAGS:
            for el in self.tree.xpath(".//%s" % tag):
                parent = el.getparent()
                if parent is not None:
                    parent.remove(el)
        return self

    def load_and_transform(self,
                           css_inline=True,
                           remove_unsafe_tags=True,
                           make_links_absolute=True,
                           set_content_type_meta=True,
                           update_stylesheet=False,
                           load_images=True,
                           images_inline=False,
                           **kw):

        if not make_links_absolute:
            # Now we use Premailer that always makes links absolute
            warnings.warn("make_links_absolute=False is deprecated.", DeprecationWarning)

        if update_stylesheet:
            # Premailer has no such feature.
            warnings.warn("update_stylesheet=True is deprecated.", DeprecationWarning)

        # 1. Premailer make some transformations on self.root tree:
        #  - load external css and make css inline
        #  - make absolute href and src if base_url is set
        if css_inline:
            self.get_premailer(**kw).transform()

        # 2. Load linked images and transform links
        # If load_images is a function, use if as callback
        if load_images:
            if is_callable(load_images):
                func = functools.partial(self._load_attachment_func, callback=load_images)
            else:
                func = self._load_attachment_func
            self.apply_to_images(func)

        # 3. Remove unsafe tags is requested
        if remove_unsafe_tags:
            self.remove_unsafe_tags()

        # 4. Set <meta> content-type
        if set_content_type_meta:
            # TODO: may be remove this ?
            self.add_content_type_meta()

        # 5. Make images inline
        if load_images and images_inline:
            self.make_all_images_inline()

        return self

    def make_all_images_inline(self):
        for a in self.attachment_store:
            a.is_inline = True
        self.synchronize_inline_images()
        return self

    def synchronize_inline_images(self, inline_names=None, non_inline_names=None):
        """
        Set img src in html for images, marked as "inline" in attachments_store
        """

        if inline_names is None or non_inline_names is None:

            inline_names = {}
            non_inline_names = {}

            for a in self.attachment_store:
                if a.is_inline:
                    inline_names[a.filename] = a.content_id
                else:
                    non_inline_names[a.content_id] = a.filename

        def _src_update_func(src, **kw):
            if src.startswith('cid:'):
                content_id = src[4:]
                if content_id in non_inline_names:
                    return non_inline_names[content_id]
            else:
                if src in inline_names:
                    return 'cid:'+inline_names[src]
            return src

        self.apply_to_images(_src_update_func)

        return self


class Transformer(BaseTransformer):
    pass


class MessageTransformer(BaseTransformer):

    def __init__(self, message, **kw):
        self.message = message

        html = message._html
        if isinstance(html, BaseTemplate):
            html = html.template_text

        params = {'html': html, 'attachment_store': message.attachments}
        params.update(kw)
        BaseTransformer.__init__(self, **params)

    def save(self):
        m = self.message
        if isinstance(m._html, BaseTemplate):
            m._html.set_template_text(self.to_string())
        else:
            m._html = self.to_string()
