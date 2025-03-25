import sys

from sentry_sdk._compat import PY2, reraise
from sentry_sdk._functools import partial
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk._werkzeug import get_host, _get_headers
from sentry_sdk.api import continue_trace
from sentry_sdk.consts import OP
from sentry_sdk.hub import Hub, _should_send_default_pii
from sentry_sdk.utils import (
    ContextVar,
    capture_internal_exceptions,
    event_from_exception,
)
from sentry_sdk.tracing import Transaction, TRANSACTION_SOURCE_ROUTE
from sentry_sdk.sessions import auto_session_tracking
from sentry_sdk.integrations._wsgi_common import _filter_headers

if TYPE_CHECKING:
    from typing import Callable
    from typing import Dict
    from typing import Iterator
    from typing import Any
    from typing import Tuple
    from typing import Optional
    from typing import TypeVar
    from typing import Protocol

    from sentry_sdk.utils import ExcInfo
    from sentry_sdk._types import Event, EventProcessor

    WsgiResponseIter = TypeVar("WsgiResponseIter")
    WsgiResponseHeaders = TypeVar("WsgiResponseHeaders")
    WsgiExcInfo = TypeVar("WsgiExcInfo")

    class StartResponse(Protocol):
        def __call__(self, status, response_headers, exc_info=None):  # type: ignore
            # type: (str, WsgiResponseHeaders, Optional[WsgiExcInfo]) -> WsgiResponseIter
            pass


_wsgi_middleware_applied = ContextVar("sentry_wsgi_middleware_applied")


if PY2:

    def wsgi_decoding_dance(s, charset="utf-8", errors="replace"):
        # type: (str, str, str) -> str
        return s.decode(charset, errors)

else:

    def wsgi_decoding_dance(s, charset="utf-8", errors="replace"):
        # type: (str, str, str) -> str
        return s.encode("latin1").decode(charset, errors)


def get_request_url(environ, use_x_forwarded_for=False):
    # type: (Dict[str, str], bool) -> str
    """Return the absolute URL without query string for the given WSGI
    environment."""
    return "%s://%s/%s" % (
        environ.get("wsgi.url_scheme"),
        get_host(environ, use_x_forwarded_for),
        wsgi_decoding_dance(environ.get("PATH_INFO") or "").lstrip("/"),
    )


class SentryWsgiMiddleware(object):
    __slots__ = ("app", "use_x_forwarded_for")

    def __init__(self, app, use_x_forwarded_for=False):
        # type: (Callable[[Dict[str, str], Callable[..., Any]], Any], bool) -> None
        self.app = app
        self.use_x_forwarded_for = use_x_forwarded_for

    def __call__(self, environ, start_response):
        # type: (Dict[str, str], Callable[..., Any]) -> _ScopedResponse
        if _wsgi_middleware_applied.get(False):
            return self.app(environ, start_response)

        _wsgi_middleware_applied.set(True)
        try:
            hub = Hub(Hub.current)
            with auto_session_tracking(hub, session_mode="request"):
                with hub:
                    with capture_internal_exceptions():
                        with hub.configure_scope() as scope:
                            scope.clear_breadcrumbs()
                            scope._name = "wsgi"
                            scope.add_event_processor(
                                _make_wsgi_event_processor(
                                    environ, self.use_x_forwarded_for
                                )
                            )

                    transaction = continue_trace(
                        environ,
                        op=OP.HTTP_SERVER,
                        name="generic WSGI request",
                        source=TRANSACTION_SOURCE_ROUTE,
                    )

                    with hub.start_transaction(
                        transaction, custom_sampling_context={"wsgi_environ": environ}
                    ):
                        try:
                            rv = self.app(
                                environ,
                                partial(
                                    _sentry_start_response, start_response, transaction
                                ),
                            )
                        except BaseException:
                            reraise(*_capture_exception(hub))
        finally:
            _wsgi_middleware_applied.set(False)

        return _ScopedResponse(hub, rv)


def _sentry_start_response(  # type: ignore
    old_start_response,  # type: StartResponse
    transaction,  # type: Transaction
    status,  # type: str
    response_headers,  # type: WsgiResponseHeaders
    exc_info=None,  # type: Optional[WsgiExcInfo]
):
    # type: (...) -> WsgiResponseIter
    with capture_internal_exceptions():
        status_int = int(status.split(" ", 1)[0])
        transaction.set_http_status(status_int)

    if exc_info is None:
        # The Django Rest Framework WSGI test client, and likely other
        # (incorrect) implementations, cannot deal with the exc_info argument
        # if one is present. Avoid providing a third argument if not necessary.
        return old_start_response(status, response_headers)
    else:
        return old_start_response(status, response_headers, exc_info)


def _get_environ(environ):
    # type: (Dict[str, str]) -> Iterator[Tuple[str, str]]
    """
    Returns our explicitly included environment variables we want to
    capture (server name, port and remote addr if pii is enabled).
    """
    keys = ["SERVER_NAME", "SERVER_PORT"]
    if _should_send_default_pii():
        # make debugging of proxy setup easier. Proxy headers are
        # in headers.
        keys += ["REMOTE_ADDR"]

    for key in keys:
        if key in environ:
            yield key, environ[key]


def get_client_ip(environ):
    # type: (Dict[str, str]) -> Optional[Any]
    """
    Infer the user IP address from various headers. This cannot be used in
    security sensitive situations since the value may be forged from a client,
    but it's good enough for the event payload.
    """
    try:
        return environ["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
    except (KeyError, IndexError):
        pass

    try:
        return environ["HTTP_X_REAL_IP"]
    except KeyError:
        pass

    return environ.get("REMOTE_ADDR")


def _capture_exception(hub):
    # type: (Hub) -> ExcInfo
    exc_info = sys.exc_info()

    # Check client here as it might have been unset while streaming response
    if hub.client is not None:
        e = exc_info[1]

        # SystemExit(0) is the only uncaught exception that is expected behavior
        should_skip_capture = isinstance(e, SystemExit) and e.code in (0, None)
        if not should_skip_capture:
            event, hint = event_from_exception(
                exc_info,
                client_options=hub.client.options,
                mechanism={"type": "wsgi", "handled": False},
            )
            hub.capture_event(event, hint=hint)

    return exc_info


class _ScopedResponse(object):
    __slots__ = ("_response", "_hub")

    def __init__(self, hub, response):
        # type: (Hub, Iterator[bytes]) -> None
        self._hub = hub
        self._response = response

    def __iter__(self):
        # type: () -> Iterator[bytes]
        iterator = iter(self._response)

        while True:
            with self._hub:
                try:
                    chunk = next(iterator)
                except StopIteration:
                    break
                except BaseException:
                    reraise(*_capture_exception(self._hub))

            yield chunk

    def close(self):
        # type: () -> None
        with self._hub:
            try:
                self._response.close()  # type: ignore
            except AttributeError:
                pass
            except BaseException:
                reraise(*_capture_exception(self._hub))


def _make_wsgi_event_processor(environ, use_x_forwarded_for):
    # type: (Dict[str, str], bool) -> EventProcessor
    # It's a bit unfortunate that we have to extract and parse the request data
    # from the environ so eagerly, but there are a few good reasons for this.
    #
    # We might be in a situation where the scope/hub never gets torn down
    # properly. In that case we will have an unnecessary strong reference to
    # all objects in the environ (some of which may take a lot of memory) when
    # we're really just interested in a few of them.
    #
    # Keeping the environment around for longer than the request lifecycle is
    # also not necessarily something uWSGI can deal with:
    # https://github.com/unbit/uwsgi/issues/1950

    client_ip = get_client_ip(environ)
    request_url = get_request_url(environ, use_x_forwarded_for)
    query_string = environ.get("QUERY_STRING")
    method = environ.get("REQUEST_METHOD")
    env = dict(_get_environ(environ))
    headers = _filter_headers(dict(_get_headers(environ)))

    def event_processor(event, hint):
        # type: (Event, Dict[str, Any]) -> Event
        with capture_internal_exceptions():
            # if the code below fails halfway through we at least have some data
            request_info = event.setdefault("request", {})

            if _should_send_default_pii():
                user_info = event.setdefault("user", {})
                if client_ip:
                    user_info.setdefault("ip_address", client_ip)

            request_info["url"] = request_url
            request_info["query_string"] = query_string
            request_info["method"] = method
            request_info["env"] = env
            request_info["headers"] = headers

        return event

    return event_processor
