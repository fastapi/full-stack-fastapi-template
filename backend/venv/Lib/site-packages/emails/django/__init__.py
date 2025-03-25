# encoding: utf-8
from __future__ import absolute_import
from django.core.mail import get_connection
from .. message import MessageTransformerMixin, MessageSignMixin, MessageBuildMixin, BaseMessage
from .. utils import sanitize_email

__all__ = ['DjangoMessageMixin', 'DjangoMessage']


class DjangoMessageMixin(object):

    _recipients = None
    _from_email = None

    @property
    def encoding(self):
        return self.charset or 'utf-8'

    def recipients(self):
        ret = self._recipients
        if ret is None:
            ret = self.get_recipients_emails()
        return [sanitize_email(e) for e in ret]

    @property
    def from_email(self):
        return sanitize_email(self._from_email or self.mail_from[1])

    def _set_emails(self, mail_to=None, set_mail_to=True, mail_from=None,
                    set_mail_from=False, to=None):

        self._recipients = None
        self._from_email = None

        mail_to = mail_to or to  # "to" is legacy

        if mail_to is not None:
            if set_mail_to:
                self.mail_to = mail_to
            else:
                self._recipients = [mail_to, ]

        if mail_from is not None:
            if set_mail_from:
                self.mail_from = mail_from
            else:
                self._from_email = mail_from

    def send(self, mail_to=None, set_mail_to=True, mail_from=None, set_mail_from=False,
             context=None, connection=None, to=None):

        self._set_emails(mail_to=mail_to, set_mail_to=set_mail_to,
                         mail_from=mail_from, set_mail_from=set_mail_from, to=to)

        if context is not None:
            self.render(**context)

        connection = connection or get_connection()
        return connection.send_messages([self, ])


class DjangoMessage(DjangoMessageMixin, MessageTransformerMixin, MessageSignMixin, MessageBuildMixin, BaseMessage):
    """
    Send via django email smtp backend
    """
    pass

Message = DjangoMessage
