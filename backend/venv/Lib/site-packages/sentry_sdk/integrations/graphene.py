from sentry_sdk.hub import Hub, _should_send_default_pii
from sentry_sdk.integrations import DidNotEnable, Integration
from sentry_sdk.utils import (
    capture_internal_exceptions,
    event_from_exception,
    package_version,
)
from sentry_sdk._types import TYPE_CHECKING


try:
    from graphene.types import schema as graphene_schema  # type: ignore
except ImportError:
    raise DidNotEnable("graphene is not installed")


if TYPE_CHECKING:
    from typing import Any, Dict, Union
    from graphene.language.source import Source  # type: ignore
    from graphql.execution import ExecutionResult  # type: ignore
    from graphql.type import GraphQLSchema  # type: ignore
    from sentry_sdk._types import Event


class GrapheneIntegration(Integration):
    identifier = "graphene"

    @staticmethod
    def setup_once():
        # type: () -> None
        version = package_version("graphene")

        if version is None:
            raise DidNotEnable("Unparsable graphene version.")

        if version < (3, 3):
            raise DidNotEnable("graphene 3.3 or newer required.")

        _patch_graphql()


def _patch_graphql():
    # type: () -> None
    old_graphql_sync = graphene_schema.graphql_sync
    old_graphql_async = graphene_schema.graphql

    def _sentry_patched_graphql_sync(schema, source, *args, **kwargs):
        # type: (GraphQLSchema, Union[str, Source], Any, Any) -> ExecutionResult
        hub = Hub.current
        integration = hub.get_integration(GrapheneIntegration)
        if integration is None:
            return old_graphql_sync(schema, source, *args, **kwargs)

        with hub.configure_scope() as scope:
            scope.add_event_processor(_event_processor)

        result = old_graphql_sync(schema, source, *args, **kwargs)

        with capture_internal_exceptions():
            for error in result.errors or []:
                event, hint = event_from_exception(
                    error,
                    client_options=hub.client.options if hub.client else None,
                    mechanism={
                        "type": integration.identifier,
                        "handled": False,
                    },
                )
                hub.capture_event(event, hint=hint)

        return result

    async def _sentry_patched_graphql_async(schema, source, *args, **kwargs):
        # type: (GraphQLSchema, Union[str, Source], Any, Any) -> ExecutionResult
        hub = Hub.current
        integration = hub.get_integration(GrapheneIntegration)
        if integration is None:
            return await old_graphql_async(schema, source, *args, **kwargs)

        with hub.configure_scope() as scope:
            scope.add_event_processor(_event_processor)

        result = await old_graphql_async(schema, source, *args, **kwargs)

        with capture_internal_exceptions():
            for error in result.errors or []:
                event, hint = event_from_exception(
                    error,
                    client_options=hub.client.options if hub.client else None,
                    mechanism={
                        "type": integration.identifier,
                        "handled": False,
                    },
                )
                hub.capture_event(event, hint=hint)

        return result

    graphene_schema.graphql_sync = _sentry_patched_graphql_sync
    graphene_schema.graphql = _sentry_patched_graphql_async


def _event_processor(event, hint):
    # type: (Event, Dict[str, Any]) -> Event
    if _should_send_default_pii():
        request_info = event.setdefault("request", {})
        request_info["api_target"] = "graphql"

    elif event.get("request", {}).get("data"):
        del event["request"]["data"]

    return event
