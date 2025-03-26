from importlib import import_module

from sentry_sdk.hub import Hub, _should_send_default_pii
from sentry_sdk.integrations import DidNotEnable, Integration
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.integrations._wsgi_common import request_body_within_bounds
from sentry_sdk.utils import (
    capture_internal_exceptions,
    event_from_exception,
    package_version,
)
from sentry_sdk._types import TYPE_CHECKING

try:
    # importing like this is necessary due to name shadowing in ariadne
    # (ariadne.graphql is also a function)
    ariadne_graphql = import_module("ariadne.graphql")
except ImportError:
    raise DidNotEnable("ariadne is not installed")


if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional
    from ariadne.types import GraphQLError, GraphQLResult, GraphQLSchema, QueryParser  # type: ignore
    from graphql.language.ast import DocumentNode  # type: ignore
    from sentry_sdk._types import Event, EventProcessor


class AriadneIntegration(Integration):
    identifier = "ariadne"

    @staticmethod
    def setup_once():
        # type: () -> None
        version = package_version("ariadne")

        if version is None:
            raise DidNotEnable("Unparsable ariadne version.")

        if version < (0, 20):
            raise DidNotEnable("ariadne 0.20 or newer required.")

        ignore_logger("ariadne")

        _patch_graphql()


def _patch_graphql():
    # type: () -> None
    old_parse_query = ariadne_graphql.parse_query
    old_handle_errors = ariadne_graphql.handle_graphql_errors
    old_handle_query_result = ariadne_graphql.handle_query_result

    def _sentry_patched_parse_query(context_value, query_parser, data):
        # type: (Optional[Any], Optional[QueryParser], Any) -> DocumentNode
        hub = Hub.current
        integration = hub.get_integration(AriadneIntegration)
        if integration is None:
            return old_parse_query(context_value, query_parser, data)

        with hub.configure_scope() as scope:
            event_processor = _make_request_event_processor(data)
            scope.add_event_processor(event_processor)

        result = old_parse_query(context_value, query_parser, data)
        return result

    def _sentry_patched_handle_graphql_errors(errors, *args, **kwargs):
        # type: (List[GraphQLError], Any, Any) -> GraphQLResult
        hub = Hub.current
        integration = hub.get_integration(AriadneIntegration)
        if integration is None:
            return old_handle_errors(errors, *args, **kwargs)

        result = old_handle_errors(errors, *args, **kwargs)

        with hub.configure_scope() as scope:
            event_processor = _make_response_event_processor(result[1])
            scope.add_event_processor(event_processor)

        if hub.client:
            with capture_internal_exceptions():
                for error in errors:
                    event, hint = event_from_exception(
                        error,
                        client_options=hub.client.options,
                        mechanism={
                            "type": integration.identifier,
                            "handled": False,
                        },
                    )
                    hub.capture_event(event, hint=hint)

        return result

    def _sentry_patched_handle_query_result(result, *args, **kwargs):
        # type: (Any, Any, Any) -> GraphQLResult
        hub = Hub.current
        integration = hub.get_integration(AriadneIntegration)
        if integration is None:
            return old_handle_query_result(result, *args, **kwargs)

        query_result = old_handle_query_result(result, *args, **kwargs)

        with hub.configure_scope() as scope:
            event_processor = _make_response_event_processor(query_result[1])
            scope.add_event_processor(event_processor)

        if hub.client:
            with capture_internal_exceptions():
                for error in result.errors or []:
                    event, hint = event_from_exception(
                        error,
                        client_options=hub.client.options,
                        mechanism={
                            "type": integration.identifier,
                            "handled": False,
                        },
                    )
                    hub.capture_event(event, hint=hint)

        return query_result

    ariadne_graphql.parse_query = _sentry_patched_parse_query  # type: ignore
    ariadne_graphql.handle_graphql_errors = _sentry_patched_handle_graphql_errors  # type: ignore
    ariadne_graphql.handle_query_result = _sentry_patched_handle_query_result  # type: ignore


def _make_request_event_processor(data):
    # type: (GraphQLSchema) -> EventProcessor
    """Add request data and api_target to events."""

    def inner(event, hint):
        # type: (Event, dict[str, Any]) -> Event
        if not isinstance(data, dict):
            return event

        with capture_internal_exceptions():
            try:
                content_length = int(
                    (data.get("headers") or {}).get("Content-Length", 0)
                )
            except (TypeError, ValueError):
                return event

            if _should_send_default_pii() and request_body_within_bounds(
                Hub.current.client, content_length
            ):
                request_info = event.setdefault("request", {})
                request_info["api_target"] = "graphql"
                request_info["data"] = data

            elif event.get("request", {}).get("data"):
                del event["request"]["data"]

        return event

    return inner


def _make_response_event_processor(response):
    # type: (Dict[str, Any]) -> EventProcessor
    """Add response data to the event's response context."""

    def inner(event, hint):
        # type: (Event, dict[str, Any]) -> Event
        with capture_internal_exceptions():
            if _should_send_default_pii() and response.get("errors"):
                contexts = event.setdefault("contexts", {})
                contexts["response"] = {
                    "data": response,
                }

        return event

    return inner
