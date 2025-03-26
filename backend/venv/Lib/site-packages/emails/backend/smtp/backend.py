# encoding: utf-8
from __future__ import unicode_literals
import smtplib
import logging
from functools import wraps
from ..response import SMTPResponse
from .client import SMTPClientWithResponse, SMTPClientWithResponse_SSL
from ...utils import DNS_NAME
from .exceptions import SMTPConnectNetworkError


__all__ = ['SMTPBackend']

logger = logging.getLogger(__name__)


class SMTPBackend(object):

    """
    SMTPBackend manages a smtp connection.
    """

    DEFAULT_SOCKET_TIMEOUT = 5

    connection_cls = SMTPClientWithResponse
    connection_ssl_cls = SMTPClientWithResponse_SSL
    response_cls = SMTPResponse

    def __init__(self, ssl=False, fail_silently=True, **kwargs):

        self.smtp_cls = ssl and self.connection_ssl_cls or self.connection_cls

        self.ssl = ssl
        self.tls = kwargs.get('tls')
        if self.ssl and self.tls:
            raise ValueError(
                "ssl/tls are mutually exclusive, so only set "
                "one of those settings to True.")

        kwargs.setdefault('timeout', self.DEFAULT_SOCKET_TIMEOUT)
        kwargs.setdefault('local_hostname', DNS_NAME.get_fqdn())
        kwargs['port'] = int(kwargs.get('port', 0))  # Issue #85

        self.smtp_cls_kwargs = kwargs

        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.fail_silently = fail_silently

        self._client = None

    def get_client(self):
        if self._client is None:
            self._client = self.smtp_cls(parent=self, **self.smtp_cls_kwargs)
        return self._client

    def close(self):

        """
        Closes the connection to the email server.
        """

        if self._client:
            try:
                self._client.quit()
            except:
                    if self.fail_silently:
                        return
                    raise
            finally:
                self._client = None

    def make_response(self, exception=None):
        return self.response_cls(backend=self, exception=exception)

    def retry_on_disconnect(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except smtplib.SMTPServerDisconnected:
                # If server disconected, clear old client
                logging.debug('SMTPServerDisconnected, retry once')
                self.close()
                return func(*args, **kwargs)
        return wrapper

    def _send(self, **kwargs):

        response = None
        try:
            client = self.get_client()
        except IOError as exc:
            response = self.make_response(exception=SMTPConnectNetworkError.from_ioerror(exc))
        except smtplib.SMTPException as exc:
            response = self.make_response(exception=exc)

        if response:
            if not self.fail_silently:
                response.raise_if_needed()
            return response
        else:
            return client.sendmail(**kwargs)

    def sendmail(self, from_addr, to_addrs, msg, mail_options=None, rcpt_options=None):

        if not to_addrs:
            return None

        if not isinstance(to_addrs, (list, tuple)):
            to_addrs = [to_addrs, ]

        send = self.retry_on_disconnect(self._send)

        response = send(from_addr=from_addr,
                        to_addrs=to_addrs,
                        msg=msg.as_string(),
                        mail_options=mail_options,
                        rcpt_options=rcpt_options)

        if not self.fail_silently:
            response.raise_if_needed()

        return response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
