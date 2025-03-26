#!C:\Users\21658\projects\full-stack-fastapi-template\backend\venv\Scripts\python.exe
# coding: utf-8

"""

Simple utility that imports html from url ang print generated rfc822 message to console.

Example usage:

    $ python make_rfc822.py \
            --url=http://lavr.github.io/python-emails/tests/campaignmonitor-samples/sample-template/template-widgets.html \
            --inline-images \
            --subject="Some subject" \
            --from-name="Sergey Lavrinenko" \
            --from-email=s@lavr.me \
            --message-id-domain=localhost \
            --add-header="X-Test-Header: Test" \
            --add-header-imported-from \
            --send-test-email-to=sergei-nko@mail.ru \
            --smtp-host=mxs.mail.ru \
            --smtp-port=25

Copyright 2013  Sergey Lavrinenko <s@lavr.me>

"""

import sys
import logging
import json
import argparse

import emails
import emails.loader
from emails.template import JinjaTemplate as T


class MakeRFC822:
    def __init__(self, options):
        self.options = options

    def _headers_from_command_line(self):
        """
        --add-header "X-Source: AAA"
        """
        r = {}
        if self.options.add_headers:
            for s in self.options.add_headers:
                (k, v) = s.split(':', 1)
                r[k] = v

        if self.options.add_header_imported_from:
            r['X-Imported-From-URL'] = self.options.url

        return r

    def _get_message(self):

        options = self.options

        if options.message_id_domain:
            message_id = emails.MessageID(domain=options.message_id_domain)
        else:
            message_id = None

        args = dict(images_inline=options.inline_images,
                    message_params=dict(headers=self._headers_from_command_line(),
                                        mail_from=(options.from_name, options.from_email),
                                        subject=T(unicode(options.subject, 'utf-8')),
                                        message_id=message_id),
                    template_cls=T)
        if options.url:
            message = emails.loader.from_url(url=options.url, **args)
        elif options.from_directory:
            message = emails.loader.from_directory(options.from_directory, **args)
        elif options.from_file:
            message = emails.loader.from_file(options.from_file, **args)
        elif options.from_zipfile:
            message = emails.loader.from_zip(options.from_zipfile, **args)
        else:
            logging.error('No message source specified.')
            sys.exit(1)

        return message

    def _send_test_email(self, message):

        options = self.options

        if options.send_test_email_to:
            logging.debug("options.send_test_email_to YES")

            smtp_params = {}
            for k in ('host', 'port', 'ssl', 'user', 'password', 'debug'):
                smtp_params[k] = getattr(options, 'smtp_%s' % k, None)

            for mail_to in options.send_test_email_to.split(','):
                r = message.send(to=mail_to, smtp=smtp_params)
                logging.debug("mail_to=%s result=%s error=%s", mail_to, r, r.error)
                if r.error:
                    raise r.error

    def _start_batch(self):

        fn = self.options.batch
        if not fn:
            return None

        if fn == '-':
            f = sys.stdin
        else:
            f = open(fn, 'rb')

        def wrapper():
            for l in f.readlines():
                l = l.strip()
                if not l:
                    continue
                try:
                    # Try to parse line as json
                    yield json.loads(l)
                except ValueError:
                    # If it is not json, we expect one word with '@' sign
                    assert len(l.split()) == 1
                    login, domain = l.split('@')  # ensure there is something email-like
                    yield {'to': l}

        return wrapper()

    def _generate_batch(self, batch, message):
        n = 0
        for values in batch:
            message.set_mail_to(values['to'])
            message.render(**values.get('data', {}))
            s = message.as_string()
            n += 1
            logging.debug('Render email to %s', '%s.eml' % n)
            open('%s.eml' % n, 'wb').write(s)

    def main(self):

        message = self._get_message()

        if self.options.batch:
            batch = self._start_batch()
            self._generate_batch(batch, message)
        else:
            if self.options.output_format == 'eml':
                print(message.as_string())
            elif self.options.output_format == 'html':
                print(message.html_body)

        self._send_test_email(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Imports html from url ang generate rfc822 message.')

    parser.add_argument("-u", "--url", metavar="URL", dest="url", action="store", default=None)
    parser.add_argument("--source-directory", dest="from_directory", action="store", default=None)
    parser.add_argument("--source-file", dest="from_file", action="store", default=None)
    parser.add_argument("--source-zipfile", dest="from_zipfile", action="store", default=None)

    parser.add_argument("-f", "--from-email", metavar="EMAIL", dest="from_email", default=None, required=True)
    parser.add_argument("-n", "--from-name", metavar="NAME", dest="from_name", default=None, required=True)
    parser.add_argument("-s", "--subject", metavar="SUBJECT", dest="subject", default=None, required=True)
    parser.add_argument("--message-id-domain", dest="message_id_domain", default=None, required=True)

    parser.add_argument("--add-header", dest="add_headers", action='append', default=None, required=False)
    parser.add_argument("--add-header-imported-from", dest="add_header_imported_from", default=False,
                        action="store_true")

    parser.add_argument("--inline-images", action="store_true", dest="inline_images", default=False)

    parser.add_argument("--output-format", dest="output_format", default='eml', choices=['eml', ])
    parser.add_argument("--log-level", dest="log_level", default="debug")

    parser.add_argument("--send-test-email-to", dest="send_test_email_to", default=None)
    parser.add_argument("--smtp-host", dest="smtp_host", default="localhost")
    parser.add_argument("--smtp-port", dest="smtp_port", default="25")
    parser.add_argument("--smtp-ssl", dest="smtp_ssl", action="store_true")
    parser.add_argument("--smtp-user", dest="smtp_user", default=None)
    parser.add_argument("--smtp-password", dest="smtp_password", default=None)
    parser.add_argument("--smtp-debug", dest="smtp_debug", action="store_true")

    parser.add_argument("--batch", dest="batch", default=None)
    parser.add_argument("--batch-start", dest="batch_start", default=None)
    parser.add_argument("--batch-limit", dest="batch_limit", default=None)

    options = parser.parse_args()

    logging.basicConfig(level=logging.getLevelName(options.log_level.upper()))

    MakeRFC822(options=options).main()
