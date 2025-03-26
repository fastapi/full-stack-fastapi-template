# coding: utf-8
from __future__ import unicode_literals

from email.utils import getaddresses

from .compat import (string_types, is_callable, formataddr as compat_formataddr, to_unicode, to_native)
from .utils import (SafeMIMEText, SafeMIMEMultipart, sanitize_address,
                    parse_name_and_email, load_email_charsets,
                    encode_header as encode_header_,
                    renderable, format_date_header, parse_name_and_email_list,
                    cached_property)
from .exc import BadHeaderError
from .backend import ObjectFactory, SMTPBackend
from .store import MemoryFileStore, BaseFile
from .signers import DKIMSigner


load_email_charsets()  # sic!


class BaseMessage(object):

    """
    Base email message with html part, text part and attachments.
    """

    attachment_cls = BaseFile
    filestore_cls = MemoryFileStore
    policy = None

    def __init__(self,
                 charset=None,
                 message_id=None,
                 date=None,
                 subject=None,
                 mail_from=None,
                 mail_to=None,
                 headers=None,
                 html=None,
                 text=None,
                 attachments=None,
                 cc=None,
                 bcc=None,
                 headers_encoding=None):

        self._attachments = None
        self.charset = charset or 'utf-8'
        self.headers_encoding = headers_encoding or 'ascii'
        self._message_id = message_id
        self.set_subject(subject)
        self.set_date(date)
        self.set_mail_from(mail_from)
        self.set_mail_to(mail_to)
        self.set_cc(cc)
        self.set_bcc(bcc)
        self.set_headers(headers)
        self.set_html(html=html)
        self.set_text(text=text)
        self.render_data = {}

        if attachments:
            for a in attachments:
                self.attachments.add(a)

    def set_mail_from(self, mail_from):
        # In: ('Alice', '<alice@me.com>' )
        self._mail_from = mail_from and parse_name_and_email(mail_from) or None

    def get_mail_from(self):
        # Out: ('Alice', '<alice@me.com>') or None
        return self._mail_from

    mail_from = property(get_mail_from, set_mail_from)

    def set_mail_to(self, mail_to):
        self._mail_to = parse_name_and_email_list(mail_to)

    def get_mail_to(self):
        return self._mail_to

    mail_to = property(get_mail_to, set_mail_to)

    def set_cc(self, addr):
        self._cc = parse_name_and_email_list(addr)

    def get_cc(self):
        return self._cc

    cc = property(get_cc, set_cc)

    def set_bcc(self, addr):
        self._bcc = parse_name_and_email_list(addr)

    def get_bcc(self):
        return self._bcc

    bcc = property(get_bcc, set_bcc)

    def get_recipients_emails(self):
        """
        Returns message recipient's emails for actual sending.
        :return: list of emails
        """
        return list(set([a[1] for a in self._mail_to] + [a[1] for a in self.cc] + [a[1] for a in self.bcc]))

    def set_headers(self, headers):
        self._headers = headers or {}

    def set_html(self, html, url=None):
        if hasattr(html, 'read'):
            html = html.read()
        self._html = html
        self._html_url = url

    def get_html(self):
        return self._html

    html = property(get_html, set_html)

    def set_text(self, text, url=None):
        if hasattr(text, 'read'):
            text = text.read()
        self._text = text
        self._text_url = url

    def get_text(self):
        return self._text

    text = property(get_text, set_text)

    @property
    @renderable
    def html_body(self):
        return self._html

    @property
    @renderable
    def text_body(self):
        return self._text

    def set_subject(self, value):
        self._subject = value

    @renderable
    def get_subject(self):
        return self._subject

    subject = property(get_subject, set_subject)

    def render(self, **kwargs):
        self.render_data = kwargs

    def set_date(self, value):
        self._date = value

    def get_date(self):
        v = self._date
        if v is False:
            return None
        if is_callable(v):
            v = v()
        if not isinstance(v, string_types):
            v = format_date_header(v)
        return v

    date = property(get_date, set_date)
    message_date = date

    @property
    def message_id(self):
        mid = self._message_id
        if mid is False:
            return None
        return is_callable(mid) and mid() or mid

    @message_id.setter
    def message_id(self, value):
        self._message_id = value

    @property
    def attachments(self):
        if self._attachments is None:
            self._attachments = self.filestore_cls(self.attachment_cls)
        return self._attachments

    def attach(self, **kwargs):
        if 'content_disposition' not in kwargs:
            kwargs['content_disposition'] = 'attachment'
        self.attachments.add(kwargs)


class MessageBuildMixin(object):

    ROOT_PREAMBLE = 'This is a multi-part message in MIME format.\n'

    # Header names that contain structured address data (RFC #5322)
    ADDRESS_HEADERS = set(['from', 'sender', 'reply-to', 'to', 'cc', 'bcc',
                           'resent-from', 'resent-sender', 'resent-to',
                           'resent-cc', 'resent-bcc'])

    before_build = None
    after_build = None

    def encode_header(self, value):
        if value:
            return encode_header_(value, self.charset)
        else:
            return value

    def encode_address_header(self, pair):
        if not pair:
            return None
        name, email = pair
        return compat_formataddr((name or '', email))

    encode_name_header = encode_address_header  # legacy name

    def set_header(self, msg, key, value, encode=True):

        if value is None:
            # TODO: may be remove header here ?
            return

        if not isinstance(value, string_types):
            value = to_unicode(value)

        # Prevent header injection
        if '\n' in value or '\r' in value:
            raise BadHeaderError("Header values can't contain newlines (got %r for header %r)" % (value, key))

        if key.lower() in self.ADDRESS_HEADERS:
            value = ', '.join(sanitize_address(addr, self.headers_encoding)
                              for addr in getaddresses((value,)))

        msg[key] = encode and self.encode_header(value) or value

    def _build_root_message(self, message_cls=None, **kw):

        msg = (message_cls or SafeMIMEMultipart)(**kw)

        if self.policy:
            msg.policy = self.policy

        msg.preamble = self.ROOT_PREAMBLE
        self.set_header(msg, 'Date', self.date, encode=False)
        self.set_header(msg, 'Message-ID', self.message_id, encode=False)

        if self._headers:
            for (name, value) in self._headers.items():
                self.set_header(msg, name, value)

        subject = self.subject
        if subject is not None:
            self.set_header(msg, 'Subject', subject)

        self.set_header(msg, 'From', self.encode_address_header(self.mail_from), encode=False)

        mail_to = self.mail_to
        if mail_to:
            self.set_header(msg, 'To', ", ".join([self.encode_address_header(addr) for addr in mail_to]), encode=False)

        if self.cc:
            self.set_header(msg, 'Cc', ", ".join([self.encode_address_header(addr) for addr in self.cc]), encode=False)

        return msg

    def _build_html_part(self):
        text = self.html_body
        if text:
            p = SafeMIMEText(text, 'html', charset=self.charset)
            p.set_charset(self.charset)
            return p

    def _build_text_part(self):
        text = self.text_body
        if text:
            p = SafeMIMEText(text, 'plain', charset=self.charset)
            p.set_charset(self.charset)
            return p

    def build_message(self, message_cls=None):

        if self.before_build:
            self.before_build(self)

        msg = self._build_root_message(message_cls)

        rel = SafeMIMEMultipart('related')
        msg.attach(rel)

        alt = SafeMIMEMultipart('alternative')
        rel.attach(alt)

        _text = self._build_text_part()
        _html = self._build_html_part()

        if not (_html or _text):
            raise ValueError("Message must contain 'html' or 'text'")

        if _text:
            alt.attach(_text)

        if _html:
            alt.attach(_html)

        for f in self.attachments:
            part = f.mime
            if part:
                if f.is_inline:
                    rel.attach(part)
                else:
                    msg.attach(part)

        if self.after_build:
            self.after_build(self, msg)

        return msg

    _build_message = build_message

    def as_message(self, message_cls=None):
        msg = self.build_message(message_cls=message_cls)
        if self._signer:
            msg = self.sign_message(msg)
        return msg

    message = as_message

    def as_string(self, message_cls=None):
        """
        Returns message as string.

        Note: this method costs one less message-to-string conversions
        for dkim in compare to self.as_message().as_string()

        Changes:
        v0.4.2: now returns bytes, not native string
        """
        r = to_native(self.build_message(message_cls=message_cls).as_string())
        if self._signer:
            r = self.sign_string(r)
        return r


class MessageSendMixin(object):

    smtp_pool_factory = ObjectFactory
    smtp_cls = SMTPBackend

    @cached_property
    def smtp_pool(self):
        return self.smtp_pool_factory(cls=self.smtp_cls)

    def send(self,
             to=None,
             set_mail_to=True,
             mail_from=None,
             set_mail_from=False,
             render=None,
             smtp_mail_options=None,
             smtp_rcpt_options=None,
             smtp=None):

        if render is not None:
            self.render(**render)

        if smtp is None:
            smtp = {'host': 'localhost', 'port': 25, 'timeout': 5}

        if isinstance(smtp, dict):
            smtp = self.smtp_pool[smtp]

        if not hasattr(smtp, 'sendmail'):
            raise ValueError(
                "smtp must be a dict or an object with method 'sendmail'. got %s" % type(smtp))

        to_addrs = None

        if to:
            if set_mail_to:
                self.set_mail_to(to)
            else:
                to_addrs = [a[1] for a in parse_name_and_email_list(to)]

        to_addrs = to_addrs or self.get_recipients_emails()

        if not to_addrs:
            raise ValueError('No to-addr')

        if mail_from:
            if set_mail_from:
                self.set_mail_from(mail_from)
                from_addr = self._mail_from[1]
            else:
                mail_from = parse_name_and_email(mail_from)
                from_addr = mail_from[1]
        else:
            from_addr = self._mail_from[1]

        if not from_addr:
            raise ValueError('No "from" addr')

        params = dict(from_addr=from_addr, to_addrs=to_addrs, msg=self,
                      mail_options=smtp_mail_options, rcpt_options=smtp_rcpt_options)

        return smtp.sendmail(**params)


class MessageTransformerMixin(object):

    transformer_cls = None
    _transformer = None

    def create_transformer(self, transformer_cls=None, **kw):
        cls = transformer_cls or self.transformer_cls
        if cls is None:
            from .transformer import MessageTransformer  # avoid cyclic import
            cls = MessageTransformer
        self._transformer = cls(message=self, **kw)
        return self._transformer

    def destroy_transformer(self):
        self._transformer = None

    @property
    def transformer(self):
        if self._transformer is None:
            self.create_transformer()
        return self._transformer

    def transform(self, **kwargs):
        self.transformer.load_and_transform(**kwargs)
        self.transformer.save()

    def set_html(self, **kw):
        # When html set, remove old transformer
        self.destroy_transformer()
        BaseMessage.set_html(self, **kw)


class MessageSignMixin(object):

    signer_cls = DKIMSigner
    _signer = None

    def sign(self, **kwargs):
        self._signer = self.signer_cls(**kwargs)
        return self

    dkim = sign

    def sign_message(self, msg):
        """
        Add sign header to email.Message
        """
        return self._signer.sign_message(msg)

    def sign_string(self, message_string):
        """
        Add sign header to message-as-a-string
        """
        return self._signer.sign_message_string(message_string)


class Message(MessageSendMixin, MessageTransformerMixin, MessageSignMixin, MessageBuildMixin, BaseMessage):
    """
    Email message with:
    - DKIM signer
    - smtp send
    - Message.transformer object
    """
    pass


def html(**kwargs):
    return Message(**kwargs)


class DjangoMessageProxy(object):

    """
    Class obsoletes with emails.django_.DjangoMessage

    Class looks like django.core.mail.EmailMessage for standard django email backend.

    Example usage:

        message = emails.Message(html='...', subject='...', mail_from='robot@company.ltd')
        connection = django.core.mail.get_connection()

        message.set_mail_to('somebody@somewhere.net')
        connection.send_messages([DjangoMessageProxy(message), ])
    """

    def __init__(self, message, recipients=None, context=None):
        self._message = message
        self._recipients = recipients
        self._context = context and context.copy() or {}

        self.from_email = message.mail_from[1]
        self.encoding = message.charset

    def recipients(self):
        return self._recipients or [r[1] for r in self._message.mail_to]

    def message(self):
        self._message.render(**self._context)
        return self._message.message()
