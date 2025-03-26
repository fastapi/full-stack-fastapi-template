"""GAE specific URL reading functions"""

__all__ = ['_defaultFetcher']

import email.message

from google.appengine.api import urlfetch

from . import errorhandler

log = errorhandler.ErrorHandler()


def _parse_header(content_type):
    msg = email.message.EmailMessage()
    msg['content-type'] = content_type
    return msg.get_content_type(), msg['content-type'].params


def _defaultFetcher(url):
    """
    uses GoogleAppEngine (GAE)
        fetch(url, payload=None, method=GET, headers={}, allow_truncated=False)

    Response
        content
            The body content of the response.
        content_was_truncated
            True if the allow_truncated parameter to fetch() was True and
            the response exceeded the maximum response size. In this case,
            the content attribute contains the truncated response.
        status_code
            The HTTP status code.
        headers
            The HTTP response headers, as a mapping of names to values.

    Exceptions
        exception InvalidURLError()
            The URL of the request was not a valid URL, or it used an
            unsupported method. Only http and https URLs are supported.
        exception DownloadError()
            There was an error retrieving the data.

            This exception is not raised if the server returns an HTTP
            error code: In that case, the response data comes back intact,
            including the error code.

        exception ResponseTooLargeError()
            The response data exceeded the maximum allowed size, and the
            allow_truncated parameter passed to fetch() was False.
    """
    try:
        r = urlfetch.fetch(url, method=urlfetch.GET)
    except urlfetch.Error as e:
        log.warn(f'Error opening url={url!r}: {e}', error=IOError)
        return

    if r.status_code != 200:
        # TODO: 301 etc
        log.warn(
            f'Error opening url={url!r}: HTTP status {r.status_code}',
            error=IOError,
        )
        return

    # find mimetype and encoding
    try:
        mimetype, params = _parse_header(r.headers['content-type'])
        encoding = params['charset']
    except KeyError:
        mimetype = 'application/octet-stream'
        encoding = None
    if mimetype != 'text/css':
        log.error(
            f'Expected "text/css" mime type for url {url!r} but found: {mimetype!r}',
            error=ValueError,
        )
    return encoding, r.content
