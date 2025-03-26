# encoding: utf-8
# This module use pydkim for DKIM signature

# For python2.4:
#  - use dkimpy v0.3 from http://hewgill.com/pydkim/
#  - install hashlib (https://pypi.python.org/pypi/hashlib/20081119) and dnspython

from __future__ import unicode_literals
import logging

from .packages import dkim
from .packages.dkim import DKIMException, UnparsableKeyError
from .packages.dkim.crypto import parse_pem_private_key
from .compat import to_bytes, to_native


class DKIMSigner:

    def __init__(self, selector, domain, key=None, ignore_sign_errors=False, **kwargs):

        self.ignore_sign_errors = ignore_sign_errors
        self._sign_params = kwargs

        privkey = key or kwargs.pop('privkey', None)  # privkey is legacy synonym for `key`

        if not privkey:
            raise TypeError("DKIMSigner.__init__() requires 'key' argument")

        if privkey and hasattr(privkey, 'read'):
            privkey = privkey.read()

        # Compile private key
        try:
            privkey = parse_pem_private_key(to_bytes(privkey))
        except UnparsableKeyError as exc:
            raise DKIMException(exc)

        self._sign_params.update({'privkey': privkey,
                                  'domain': to_bytes(domain),
                                  'selector': to_bytes(selector)})

    def get_sign_string(self, message):

        try:
            # pydkim module parses message and privkey on each signing
            # this is not optimal for mass operations
            # TODO: patch pydkim or use another signing module
            return dkim.sign(message=message, **self._sign_params)
        except DKIMException:
            if self.ignore_sign_errors:
                logging.exception('Error signing message')
            else:
                raise

    def get_sign_header(self, message):
        # pydkim returns string, so we should split
        s = self.get_sign_string(message)
        if s:
            (header, value) = to_native(s).split(': ', 1)
            if value.endswith("\r\n"):
                value = value[:-2]
            return header, value

    def sign_message(self, msg):
        """
        Add DKIM header to email.message
        """

        # py3 pydkim requires bytes to compute dkim header
        # but py3 smtplib requires str to send DATA command (#
        # so we have to convert msg.as_string

        dkim_header = self.get_sign_header(to_bytes(msg.as_string()))
        if dkim_header:
            msg._headers.insert(0, dkim_header)
        return msg

    def sign_message_string(self, message_string):
        """
        Insert DKIM header to message string
        """

        # py3 pydkim requires bytes to compute dkim header
        # but py3 smtplib requires str to send DATA command
        # so we have to convert message_string

        s = self.get_sign_string(to_bytes(message_string))
        return s and to_native(s) + message_string or message_string

