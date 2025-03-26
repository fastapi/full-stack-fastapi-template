# encoding: utf-8
__all__ = ['SMTPClientWithResponse', 'SMTPClientWithResponse_SSL']

import smtplib
from smtplib import _have_ssl, SMTP
import logging
from ... utils import sanitize_email

logger = logging.getLogger(__name__)


class SMTPClientWithResponse(SMTP):

    def __init__(self, parent, **kwargs):

        self._initialized = False

        self.parent = parent
        self.make_response = parent.make_response
        self.tls = kwargs.pop('tls', False)
        self.ssl = kwargs.pop('ssl', False)
        self.debug = kwargs.pop('debug', 0)
        self.user = kwargs.pop('user', None)
        self.password = kwargs.pop('password', None)

        SMTP.__init__(self, **kwargs)

        self.initialize()

    def initialize(self):
        if not self._initialized:
            self.set_debuglevel(self.debug)
            if self.tls:
                self.starttls()
            if self.user:
                self.login(user=self.user, password=self.password)
            self.ehlo_or_helo_if_needed()
            self.initialized = True

    def quit(self):
        """Closes the connection to the email server."""
        try:
            SMTP.quit(self)
        except (smtplib.SMTPServerDisconnected, ):
            self.close()

    def _rset(self):
        try:
            self.rset()
        except smtplib.SMTPServerDisconnected:
            pass

    def sendmail(self, from_addr, to_addrs, msg, mail_options=None, rcpt_options=None):

        if not to_addrs:
            return None

        rcpt_options = rcpt_options or []
        mail_options = mail_options or []
        esmtp_opts = []
        if self.does_esmtp:
            if self.has_extn('size'):
                esmtp_opts.append("size=%d" % len(msg))
            for option in mail_options:
                esmtp_opts.append(option)

        response = self.make_response()

        from_addr = sanitize_email(from_addr)

        response.from_addr = from_addr
        response.esmtp_opts = esmtp_opts[:]

        (code, resp) = self.mail(from_addr, esmtp_opts)
        response.set_status('mail', code, resp)

        if code != 250:
            self._rset()
            exc = smtplib.SMTPSenderRefused(code, resp, from_addr)
            response.set_exception(exc)
            return response

        if not isinstance(to_addrs, (list, tuple)):
            to_addrs = [to_addrs]

        to_addrs = [sanitize_email(e) for e in to_addrs]

        response.to_addrs = to_addrs
        response.rcpt_options = rcpt_options[:]
        response.refused_recipients = {}

        for a in to_addrs:
            (code, resp) = self.rcpt(a, rcpt_options)
            response.set_status('rcpt', code, resp, recipient=a)
            if (code != 250) and (code != 251):
                response.refused_recipients[a] = (code, resp)

        if len(response.refused_recipients) == len(to_addrs):
            # the server refused all our recipients
            self._rset()
            exc = smtplib.SMTPRecipientsRefused(response.refused_recipients)
            response.set_exception(exc)
            return response

        (code, resp) = self.data(msg)
        response.set_status('data', code, resp)
        if code != 250:
            self._rset()
            exc = smtplib.SMTPDataError(code, resp)
            response.set_exception(exc)
            return response

        response._finished = True
        return response


if _have_ssl:

    from smtplib import SMTP_SSL
    import ssl

    class SMTPClientWithResponse_SSL(SMTP_SSL, SMTPClientWithResponse):

        def __init__(self, **kw):
            args = {}
            for k in ('host', 'port', 'local_hostname', 'keyfile', 'certfile', 'timeout'):
                if k in kw:
                    args[k] = kw[k]
            SMTP_SSL.__init__(self, **args)
            SMTPClientWithResponse.__init__(self, **kw)

        def _rset(self):
            try:
                self.rset()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                pass

        def quit(self):
            """Closes the connection to the email server."""
            try:
                SMTPClientWithResponse.quit(self)
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the server.
                self.close()

        def sendmail(self, *args, **kw):
            return SMTPClientWithResponse.sendmail(self, *args, **kw)

else:

    class SMTPClientWithResponse_SSL:
        def __init__(self, *args, **kwargs):
            # should raise import error here
            import ssl



