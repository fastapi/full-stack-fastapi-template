# coding: utf-8
"""
python-emails
~~~~~~~~~~~~~

Modern python library for email.

Build message:

   >>> import emails
   >>> message = emails.html(html="<p>Hi!<br>Here is your receipt...",
                          subject="Your receipt No. 567098123",
                          mail_from=('Some Store', 'store@somestore.com'))
   >>> message.attach(data=open('bill.pdf'), filename='bill.pdf')

send message and get response from smtp server:

   >>> r = message.send(to='s@lavr.me', smtp={'host': 'aspmx.l.google.com', 'timeout': 5})
   >>> assert r.status_code == 250

and more:

 * DKIM signature
 * Render body from template
 * Flask extension and Django integration
 * Message body transformation methods
 * Load message from url or from file


Links
`````

* `documentation <http://python-emails.readthedocs.org/>`_
* `source code <http://github.com/lavr/python-emails>`_

"""

from __future__ import unicode_literals

__title__ = 'emails'
__version__ = '0.6'
__author__ = 'Sergey Lavrinenko'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013-2019 Sergey Lavrinenko'

USER_AGENT = 'python-emails/%s' % __version__

from .message import Message, html
from .utils import MessageID


