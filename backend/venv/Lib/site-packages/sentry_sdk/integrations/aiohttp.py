import sys
import weakref

from sentry_sdk.api import continue_trace
from sentry_sdk._compat import reraise
from sentry_sdk.consts import OP, SPANDATA
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration, DidNotEnable
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.sessions import auto_session_tracking
from sentry_sdk.integrations._wsgi_common import (
    _filter_headers,
    request_body_within_bounds,
)
from sentry_sdk.tracing import (
    BAGGAGE_HEADER_NAME,
    SOURCE_FOR_STYLE,
    TRANSACTION_SOURCE_ROUTE,
)
from sentry_sdk.tracing_utils import should_propagate_trace
from sentry_sdk.utils import (
    capture_internal_exceptions,
    event_from_exception,
    logger,
    parse_url,
    parse_version,
    transaction_from_function,
    HAS_REAL_CONTEXTVARS,
    CONTEXTVARS_ERROR_MESSAGE,
    SENSITIVE_DATA_SUBSTITUTE,
    AnnotatedValue,
)

try:
    import asyncio

    from aiohttp import __version__ as AIOHTTP_VERSION
    from aiohttp import ClientSession, TraceConfig
    from aiohttp.web import Application, HTTPException, UrlDispatcher
except ImportError:
    raise DidNotEnable("AIOHTTP not installed")

from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp.web_request import Request
    from aiohttp.web_urldispatcher import UrlMappingMatchInfo
    from aiohttp import TraceRequestStartParams, TraceRequestEndParams
    from types import SimpleNamespace
    from typing import Any
    from typing import Optional
    from typing import Tuple
    from typing import Union

    from sentry_sdk.utils import ExcInfo
    from sentry_sdk._types import Event, EventProcessor


TRANSACTION_STYLE_VALUES = ("handler_name", "method_and_path_pattern")


class AioHttpIntegration(Integration):
    identifier = "aiohttp"

    def __init__(self, transaction_style="handler_name"):
        # type: (str) -> None
        if transaction_style not in TRANSACTION_STYLE_VALUES:
            raise ValueError(
                "Invalid value for transaction_style: %s (must be in %s)"
                % (transaction_style, TRANSACTION_STYLE_VALUES)
            )
        self.transaction_style = transaction_style

    @staticmethod
    def setup_once():
        # type: () -> None

        version = parse_version(AIOHTTP_VERSION)

        if version is None:
            raise DidNotEnable("Unparsable AIOHTTP version: {}".format(AIOHTTP_VERSION))

        if version < (3, 4):
            raise DidNotEnable("AIOHTTP 3.4 or newer required.")

        if not HAS_REAL_CONTEXTVARS:
            # We better have contextvars or we're going to leak state between
            # requests.
            raise DidNotEnable(
                "The aiohttp integration for Sentry requires Python 3.7+ "
                " or aiocontextvars package." + CONTEXTVARS_ERROR_MESSAGE
            )

        ignore_logger("aiohttp.server")

        old_handle = Application._handle

        async def sentry_app_handle(self, request, *args, **kwargs):
            # type: (Any, Request, *Any, **Any) -> Any
            hub = Hub.current
            if hub.get_integration(AioHttpIntegration) is None:
                return await old_handle(self, request, *args, **kwargs)

            weak_request = weakref.ref(request)

            with Hub(hub) as hub:
                with auto_session_tracking(hub, session_mode="request"):
                    # Scope data will not leak between requests because aiohttp
                    # create a task to wrap each request.
                    with hub.configure_scope() as scope:
                        scope.clear_breadcrumbs()
                        scope.add_event_processor(_make_request_processor(weak_request))

                    headers = dict(request.headers)
                    transaction = continue_trace(
                        headers,
                        op=OP.HTTP_SERVER,
                        # If this transaction name makes it to the UI, AIOHTTP's
                        # URL resolver did not find a route or died trying.
                        name="generic AIOHTTP request",
                        source=TRANSACTION_SOURCE_ROUTE,
                    )
                    with hub.start_transaction(
                        transaction,
                        custom_sampling_context={"aiohttp_request": request},
                    ):
                        try:
                            response = await old_handle(self, request)
                        except HTTPException as e:
                            transaction.set_http_status(e.status_code)
                            raise
                        except (asyncio.CancelledError, ConnectionResetError):
                            transaction.set_status("cancelled")
                            raise
                        except Exception:
                            # This will probably map to a 500 but seems like we
                            # have no way to tell. Do not set span status.
                            reraise(*_capture_exception(hub))

                        transaction.set_http_status(response.status)
                        return response

        Application._handle = sentry_app_handle

        old_urldispatcher_resolve = UrlDispatcher.resolve

        async def sentry_urldispatcher_resolve(self, request):
            # type: (UrlDispatcher, Request) -> UrlMappingMatchInfo
            rv = await old_urldispatcher_resolve(self, request)

            hub = Hub.current
            integration = hub.get_integration(AioHttpIntegration)

            name = None

            try:
                if integration.transaction_style == "handler_name":
                    name = transaction_from_function(rv.handler)
                elif integration.transaction_style == "method_and_path_pattern":
                    route_info = rv.get_info()
                    pattern = route_info.get("path") or route_info.get("formatter")
                    name = "{} {}".format(request.method, pattern)
            except Exception:
                pass

            if name is not None:
                with Hub.current.configure_scope() as scope:
                    scope.set_transaction_name(
                        name,
                        source=SOURCE_FOR_STYLE[integration.transaction_style],
                    )

            return rv

        UrlDispatcher.resolve = sentry_urldispatcher_resolve

        old_client_session_init = ClientSession.__init__

        def init(*args, **kwargs):
            # type: (Any, Any) -> None
            hub = Hub.current
            if hub.get_integration(AioHttpIntegration) is None:
                return old_client_session_init(*args, **kwargs)

            client_trace_configs = list(kwargs.get("trace_configs") or ())
            trace_config = create_trace_config()
            client_trace_configs.append(trace_config)

            kwargs["trace_configs"] = client_trace_configs
            return old_client_session_init(*args, **kwargs)

        ClientSession.__init__ = init


def create_trace_config():
    # type: () -> TraceConfig
    async def on_request_start(session, trace_config_ctx, params):
        # type: (ClientSession, SimpleNamespace, TraceRequestStartParams) -> None
        hub = Hub.current
        if hub.get_integration(AioHttpIntegration) is None:
            return

        method = params.method.upper()

        parsed_url = None
        with capture_internal_exceptions():
            parsed_url = parse_url(str(params.url), sanitize=False)

        span = hub.start_span(
            op=OP.HTTP_CLIENT,
            description="%s %s"
            % (method, parsed_url.url if parsed_url else SENSITIVE_DATA_SUBSTITUTE),
        )
        span.set_data(SPANDATA.HTTP_METHOD, method)
        if parsed_url is not None:
            span.set_data("url", parsed_url.url)
            span.set_data(SPANDATA.HTTP_QUERY, parsed_url.query)
            span.set_data(SPANDATA.HTTP_FRAGMENT, parsed_url.fragment)

        if should_propagate_trace(hub, str(params.url)):
            for key, value in hub.iter_trace_propagation_headers(span):
                logger.debug(
                    "[Tracing] Adding `{key}` header {value} to outgoing request to {url}.".format(
                        key=key, value=value, url=params.url
                    )
                )
                if key == BAGGAGE_HEADER_NAME and params.headers.get(
                    BAGGAGE_HEADER_NAME
                ):
                    # do not overwrite any existing baggage, just append to it
                    params.headers[key] += "," + value
                else:
                    params.headers[key] = value

        trace_config_ctx.span = span

    async def on_request_end(session, trace_config_ctx, params):
        # type: (ClientSession, SimpleNamespace, TraceRequestEndParams) -> None
        if trace_config_ctx.span is None:
            return

        span = trace_config_ctx.span
        span.set_http_status(int(params.response.status))
        span.set_data("reason", params.response.reason)
        span.finish()

    trace_config = TraceConfig()

    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)

    return trace_config


def _make_request_processor(weak_request):
    # type: (weakref.ReferenceType[Request]) -> EventProcessor
    def aiohttp_processor(
        event,  # type: Event
        hint,  # type: dict[str, Tuple[type, BaseException, Any]]
    ):
        # type: (...) -> Event
        request = weak_request()
        if request is None:
            return event

        with capture_internal_exceptions():
            request_info = event.setdefault("request", {})

            request_info["url"] = "%s://%s%s" % (
                request.scheme,
                request.host,
                request.path,
            )

            request_info["query_string"] = request.query_string
            request_info["method"] = request.method
            request_info["env"] = {"REMOTE_ADDR": request.remote}

            hub = Hub.current
            request_info["headers"] = _filter_headers(dict(request.headers))

            # Just attach raw data here if it is within bounds, if available.
            # Unfortunately there's no way to get structured data from aiohttp
            # without awaiting on some coroutine.
            request_info["data"] = get_aiohttp_request_data(hub, request)

        return event

    return aiohttp_processor


def _capture_exception(hub):
    # type: (Hub) -> ExcInfo
    exc_info = sys.exc_info()
    event, hint = event_from_exception(
        exc_info,
        client_options=hub.client.options,  # type: ignore
        mechanism={"type": "aiohttp", "handled": False},
    )
    hub.capture_event(event, hint=hint)
    return exc_info


BODY_NOT_READ_MESSAGE = "[Can't show request body due to implementation details.]"


def get_aiohttp_request_data(hub, request):
    # type: (Hub, Request) -> Union[Optional[str], AnnotatedValue]
    bytes_body = request._read_bytes

    if bytes_body is not None:
        # we have body to show
        if not request_body_within_bounds(hub.client, len(bytes_body)):
            return AnnotatedValue.removed_because_over_size_limit()

        encoding = request.charset or "utf-8"
        return bytes_body.decode(encoding, "replace")

    if request.can_read_body:
        # body exists but we can't show it
        return BODY_NOT_READ_MESSAGE

    # request has no body
    return None
