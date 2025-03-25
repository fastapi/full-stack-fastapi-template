from sentry_sdk import Hub
from sentry_sdk.consts import OP, SPANDATA
from sentry_sdk.integrations import Integration, DidNotEnable
from sentry_sdk.tracing import BAGGAGE_HEADER_NAME
from sentry_sdk.tracing_utils import should_propagate_trace
from sentry_sdk.utils import (
    SENSITIVE_DATA_SUBSTITUTE,
    capture_internal_exceptions,
    logger,
    parse_url,
)

from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


try:
    from httpx import AsyncClient, Client, Request, Response  # type: ignore
except ImportError:
    raise DidNotEnable("httpx is not installed")

__all__ = ["HttpxIntegration"]


class HttpxIntegration(Integration):
    identifier = "httpx"

    @staticmethod
    def setup_once():
        # type: () -> None
        """
        httpx has its own transport layer and can be customized when needed,
        so patch Client.send and AsyncClient.send to support both synchronous and async interfaces.
        """
        _install_httpx_client()
        _install_httpx_async_client()


def _install_httpx_client():
    # type: () -> None
    real_send = Client.send

    def send(self, request, **kwargs):
        # type: (Client, Request, **Any) -> Response
        hub = Hub.current
        if hub.get_integration(HttpxIntegration) is None:
            return real_send(self, request, **kwargs)

        parsed_url = None
        with capture_internal_exceptions():
            parsed_url = parse_url(str(request.url), sanitize=False)

        with hub.start_span(
            op=OP.HTTP_CLIENT,
            description="%s %s"
            % (
                request.method,
                parsed_url.url if parsed_url else SENSITIVE_DATA_SUBSTITUTE,
            ),
        ) as span:
            span.set_data(SPANDATA.HTTP_METHOD, request.method)
            if parsed_url is not None:
                span.set_data("url", parsed_url.url)
                span.set_data(SPANDATA.HTTP_QUERY, parsed_url.query)
                span.set_data(SPANDATA.HTTP_FRAGMENT, parsed_url.fragment)

            if should_propagate_trace(hub, str(request.url)):
                for key, value in hub.iter_trace_propagation_headers():
                    logger.debug(
                        "[Tracing] Adding `{key}` header {value} to outgoing request to {url}.".format(
                            key=key, value=value, url=request.url
                        )
                    )
                    if key == BAGGAGE_HEADER_NAME and request.headers.get(
                        BAGGAGE_HEADER_NAME
                    ):
                        # do not overwrite any existing baggage, just append to it
                        request.headers[key] += "," + value
                    else:
                        request.headers[key] = value

            rv = real_send(self, request, **kwargs)

            span.set_http_status(rv.status_code)
            span.set_data("reason", rv.reason_phrase)

            return rv

    Client.send = send


def _install_httpx_async_client():
    # type: () -> None
    real_send = AsyncClient.send

    async def send(self, request, **kwargs):
        # type: (AsyncClient, Request, **Any) -> Response
        hub = Hub.current
        if hub.get_integration(HttpxIntegration) is None:
            return await real_send(self, request, **kwargs)

        parsed_url = None
        with capture_internal_exceptions():
            parsed_url = parse_url(str(request.url), sanitize=False)

        with hub.start_span(
            op=OP.HTTP_CLIENT,
            description="%s %s"
            % (
                request.method,
                parsed_url.url if parsed_url else SENSITIVE_DATA_SUBSTITUTE,
            ),
        ) as span:
            span.set_data(SPANDATA.HTTP_METHOD, request.method)
            if parsed_url is not None:
                span.set_data("url", parsed_url.url)
                span.set_data(SPANDATA.HTTP_QUERY, parsed_url.query)
                span.set_data(SPANDATA.HTTP_FRAGMENT, parsed_url.fragment)

            if should_propagate_trace(hub, str(request.url)):
                for key, value in hub.iter_trace_propagation_headers():
                    logger.debug(
                        "[Tracing] Adding `{key}` header {value} to outgoing request to {url}.".format(
                            key=key, value=value, url=request.url
                        )
                    )
                    if key == BAGGAGE_HEADER_NAME and request.headers.get(
                        BAGGAGE_HEADER_NAME
                    ):
                        # do not overwrite any existing baggage, just append to it
                        request.headers[key] += "," + value
                    else:
                        request.headers[key] = value

            rv = await real_send(self, request, **kwargs)

            span.set_http_status(rv.status_code)
            span.set_data("reason", rv.reason_phrase)

            return rv

    AsyncClient.send = send
