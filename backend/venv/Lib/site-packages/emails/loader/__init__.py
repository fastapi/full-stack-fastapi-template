# encoding: utf-8
import os.path
from email.utils import formataddr

from ..compat import to_unicode, to_native
from ..compat import urlparse
from ..message import Message
from ..utils import fetch_url
from .local_store import (FileSystemLoader, ZipLoader, MsgLoader, FileNotFound)
from .helpers import guess_charset

class LoadError(Exception):
    pass


class IndexFileNotFound(LoadError):
    pass


class InvalidHtmlFile(LoadError):
    pass


def from_html(html, text=None, base_url=None, message_params=None, local_loader=None,
              template_cls=None, message_cls=None, source_filename=None, requests_params=None,
              **kwargs):

    """
    Loads message from html string with images from local_loader.

    :param html: html string
    :param base_url: base_url for html
    :param text: text string or None
    :param template_cls: if set, html and text are set with this template class
    :param local_loader: loader with local files
    :param message_cls: default is emails.Message
    :param message_params: parameters for Message constructor
    :param source_filename: source html file name (used for exception description on html parsing error)
    :param requests_params: parameters for external url handling
    :param kwargs: arguments for transformer.load_and_transform
    :return:
    """

    if template_cls is None:
        template_cls = lambda x: x

    message_params = message_params or {}

    _param_html = message_params.pop('html', None)
    _param_text = message_params.pop('text', None)

    message = (message_cls or Message)(html=template_cls(html or _param_html or ''),
                                       text=template_cls(text or _param_text),
                                       **message_params)
    message.create_transformer(requests_params=requests_params,
                               base_url=base_url,
                               local_loader=local_loader)
    if message.transformer.tree is None:
        raise InvalidHtmlFile("Error parsing '%s'" % source_filename)
    message.transformer.load_and_transform(**kwargs)
    message.transformer.save()
    message._loader = local_loader
    return message


from_string = from_html


def from_url(url, requests_params=None, **kwargs):

    def _extract_base_url(url):
        # /a/b.html -> /a
        p = list(urlparse.urlparse(url))[:5]
        p[2] = os.path.split(p[2])[0]
        return urlparse.urlunsplit(p)

    # Load html page
    r = fetch_url(url, requests_args=requests_params)
    html = r.content
    html = to_unicode(html, charset=guess_charset(r.headers, html))
    html = html.replace('\r\n', '\n')  # Remove \r

    return from_html(html,
                     base_url=_extract_base_url(url),
                     source_filename=url,
                     requests_params=requests_params,
                     **kwargs)


load_url = from_url


def _from_filebased_source(store, skip_html=False, html_filename=None, skip_text=True, text_filename=None,
                           message_params=None, **kwargs):
    """
    Loads message from prepared store `store`.

    :param store: prepared filestore
    :param skip_html: if True, make message without html part
    :param html_filename: html part filename. If None, search automatically.
    :param skip_text: if True, make message without text part
    :param text_filename: text part filename. If None, search automatically.
    :param message_params: parameters for Message
    :param kwargs: arguments for from_html
    :return:
    """

    if not skip_html:
        try:
            html_filename = store.find_index_html(html_filename)
        except FileNotFound:
            raise IndexFileNotFound('html file not found')

    dirname, html_filename = os.path.split(html_filename)
    if dirname:
        store.base_path = dirname

    html = store.content(html_filename, is_html=True, guess_charset=True)

    text = None
    if not skip_text:
        text_filename = store.find_index_text(text_filename)
        text = text_filename and store.content(text_filename) or None

    return from_html(html=html,
                     text=text,
                     local_loader=store,
                     source_filename=html_filename,
                     message_params=message_params,
                     **kwargs)


def from_directory(directory, loader_cls=None, **kwargs):
    """
    Loads message from local directory.
    Can guess for html and text part filenames (if parameters set).

    :param directory: directory path
    :param kwargs: arguments for _from_filebased_source function
    :return: emails.Message object
    """

    loader_cls = loader_cls or FileSystemLoader
    return _from_filebased_source(store=loader_cls(searchpath=directory), **kwargs)


def from_file(filename, **kwargs):
    """
    Loads message from local file.
    File `filename` must be html file.

    :param filename: filename
    :param kwargs: arguments for _from_filebased_source function
    :return: emails.Message object
    """
    return from_directory(directory=os.path.dirname(filename), html_filename=os.path.basename(filename), **kwargs)


def from_zip(zip_file, loader_cls=None, **kwargs):
    """
    Loads message from zipfile.

    :param zip_file: file-like object with zip file
    :param kwargs: arguments for _from_filebased_source function
    :return: emails.Message object
    """
    loader_cls = loader_cls or ZipLoader
    return _from_filebased_source(store=loader_cls(file=zip_file), **kwargs)


def from_rfc822(msg, loader_cls=None, message_params=None, parse_headers=False):
    # Warning: from_rfc822 is for demo purposes only
    message_params = message_params or {}
    loader_cls = loader_cls or MsgLoader

    loader = loader_cls(msg=msg)
    message = Message(html=loader.html, text=loader.text, **message_params)
    message._loader = loader

    for att in loader.attachments:
        message.attachments.add(att)

    if parse_headers:
        loader.copy_headers_to_message(message)

    return message