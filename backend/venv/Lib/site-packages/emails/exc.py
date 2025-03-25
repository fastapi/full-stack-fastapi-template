# encoding: utf-8

from .packages.dkim import DKIMException


class HTTPLoaderError(Exception):
    pass


class BadHeaderError(ValueError):
    pass


class IncompleteMessage(ValueError):
    pass