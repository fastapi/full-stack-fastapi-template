import hashlib
from functools import cached_property
from inspect import isawaitable
from sentry_sdk import configure_scope, start_span
from sentry_sdk.consts import OP
from sentry_sdk.integrations import Integration, DidNotEnable
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.hub import Hub, _should_send_default_pii
from sentry_sdk.utils import (
    capture_internal_exceptions,
    event_from_exception,
    logger,
    package_version,
    _get_installed_modules,
)
from sentry_sdk._types import TYPE_CHECKING

try:
    import strawberry.schema.schema as strawberry_schema  # type: ignore
    from strawberry import Schema
    from strawberry.extensions import SchemaExtension  # type: ignore
    from strawberry.extensions.tracing.utils import should_skip_tracing as strawberry_should_skip_tracing  # type: ignore
    from strawberry.extensions.tracing import (  # type: ignore
        SentryTracingExtension as StrawberrySentryAsyncExtension,
        SentryTracingExtensionSync as StrawberrySentrySyncExtension,
    )
    from strawberry.http import async_base_view, sync_base_view  # type: ignore
except ImportError:
    raise DidNotEnable("strawberry-graphql is not installed")

if TYPE_CHECKING:
    from typing import Any, Callable, Generator, List, Optional
    from graphql import GraphQLError, GraphQLResolveInfo  # type: ignore
    from strawberry.http import GraphQLHTTPResponse
    from strawberry.types import ExecutionContext, ExecutionResult  # type: ignore
    from sentry_sdk._types import Event, EventProcessor


ignore_logger("strawberry.execution")


class StrawberryIntegration(Integration):
    identifier = "strawberry"

    def __init__(self, async_execution=None):
        # type: (Optional[bool]) -> None
        if async_execution not in (None, False, True):
            raise ValueError(
                'Invalid value for async_execution: "{}" (must be bool)'.format(
                    async_execution
                )
            )
        self.async_execution = async_execution

    @staticmethod
    def setup_once():
        # type: () -> None
        version = package_version("strawberry-graphql")

        if version is None:
            raise DidNotEnable(
                "Unparsable strawberry-graphql version: {}".format(version)
            )

        if version < (0, 209, 5):
            raise DidNotEnable("strawberry-graphql 0.209.5 or newer required.")

        _patch_schema_init()
        _patch_execute()
        _patch_views()


def _patch_schema_init():
    # type: () -> None
    old_schema_init = Schema.__init__

    def _sentry_patched_schema_init(self, *args, **kwargs):
        # type: (Schema, Any, Any) -> None
        integration = Hub.current.get_integration(StrawberryIntegration)
        if integration is None:
            return old_schema_init(self, *args, **kwargs)

        extensions = kwargs.get("extensions") or []

        if integration.async_execution is not None:
            should_use_async_extension = integration.async_execution
        else:
            # try to figure it out ourselves
            should_use_async_extension = _guess_if_using_async(extensions)

            logger.info(
                "Assuming strawberry is running %s. If not, initialize it as StrawberryIntegration(async_execution=%s).",
                "async" if should_use_async_extension else "sync",
                "False" if should_use_async_extension else "True",
            )

        # remove the built in strawberry sentry extension, if present
        extensions = [
            extension
            for extension in extensions
            if extension
            not in (StrawberrySentryAsyncExtension, StrawberrySentrySyncExtension)
        ]

        # add our extension
        extensions.append(
            SentryAsyncExtension if should_use_async_extension else SentrySyncExtension
        )

        kwargs["extensions"] = extensions

        return old_schema_init(self, *args, **kwargs)

    Schema.__init__ = _sentry_patched_schema_init


class SentryAsyncExtension(SchemaExtension):  # type: ignore
    def __init__(
        self,
        *,
        execution_context=None,
    ):
        # type: (Any, Optional[ExecutionContext]) -> None
        if execution_context:
            self.execution_context = execution_context

    @cached_property
    def _resource_name(self):
        # type: () -> str
        query_hash = self.hash_query(self.execution_context.query)

        if self.execution_context.operation_name:
            return "{}:{}".format(self.execution_context.operation_name, query_hash)

        return query_hash

    def hash_query(self, query):
        # type: (str) -> str
        return hashlib.md5(query.encode("utf-8")).hexdigest()

    def on_operation(self):
        # type: () -> Generator[None, None, None]
        self._operation_name = self.execution_context.operation_name

        operation_type = "query"
        op = OP.GRAPHQL_QUERY

        if self.execution_context.query is None:
            self.execution_context.query = ""

        if self.execution_context.query.strip().startswith("mutation"):
            operation_type = "mutation"
            op = OP.GRAPHQL_MUTATION
        elif self.execution_context.query.strip().startswith("subscription"):
            operation_type = "subscription"
            op = OP.GRAPHQL_SUBSCRIPTION

        description = operation_type
        if self._operation_name:
            description += " {}".format(self._operation_name)

        Hub.current.add_breadcrumb(
            category="graphql.operation",
            data={
                "operation_name": self._operation_name,
                "operation_type": operation_type,
            },
        )

        with configure_scope() as scope:
            if scope.span:
                self.graphql_span = scope.span.start_child(
                    op=op, description=description
                )
            else:
                self.graphql_span = start_span(op=op, description=description)

        self.graphql_span.set_data("graphql.operation.type", operation_type)
        self.graphql_span.set_data("graphql.operation.name", self._operation_name)
        self.graphql_span.set_data("graphql.document", self.execution_context.query)
        self.graphql_span.set_data("graphql.resource_name", self._resource_name)

        yield

        self.graphql_span.finish()

    def on_validate(self):
        # type: () -> Generator[None, None, None]
        self.validation_span = self.graphql_span.start_child(
            op=OP.GRAPHQL_VALIDATE, description="validation"
        )

        yield

        self.validation_span.finish()

    def on_parse(self):
        # type: () -> Generator[None, None, None]
        self.parsing_span = self.graphql_span.start_child(
            op=OP.GRAPHQL_PARSE, description="parsing"
        )

        yield

        self.parsing_span.finish()

    def should_skip_tracing(self, _next, info):
        # type: (Callable[[Any, GraphQLResolveInfo, Any, Any], Any], GraphQLResolveInfo) -> bool
        return strawberry_should_skip_tracing(_next, info)

    async def _resolve(self, _next, root, info, *args, **kwargs):
        # type: (Callable[[Any, GraphQLResolveInfo, Any, Any], Any], Any, GraphQLResolveInfo, str, Any) -> Any
        result = _next(root, info, *args, **kwargs)

        if isawaitable(result):
            result = await result

        return result

    async def resolve(self, _next, root, info, *args, **kwargs):
        # type: (Callable[[Any, GraphQLResolveInfo, Any, Any], Any], Any, GraphQLResolveInfo, str, Any) -> Any
        if self.should_skip_tracing(_next, info):
            return await self._resolve(_next, root, info, *args, **kwargs)

        field_path = "{}.{}".format(info.parent_type, info.field_name)

        with self.graphql_span.start_child(
            op=OP.GRAPHQL_RESOLVE, description="resolving {}".format(field_path)
        ) as span:
            span.set_data("graphql.field_name", info.field_name)
            span.set_data("graphql.parent_type", info.parent_type.name)
            span.set_data("graphql.field_path", field_path)
            span.set_data("graphql.path", ".".join(map(str, info.path.as_list())))

            return await self._resolve(_next, root, info, *args, **kwargs)


class SentrySyncExtension(SentryAsyncExtension):
    def resolve(self, _next, root, info, *args, **kwargs):
        # type: (Callable[[Any, Any, Any, Any], Any], Any, GraphQLResolveInfo, str, Any) -> Any
        if self.should_skip_tracing(_next, info):
            return _next(root, info, *args, **kwargs)

        field_path = "{}.{}".format(info.parent_type, info.field_name)

        with self.graphql_span.start_child(
            op=OP.GRAPHQL_RESOLVE, description="resolving {}".format(field_path)
        ) as span:
            span.set_data("graphql.field_name", info.field_name)
            span.set_data("graphql.parent_type", info.parent_type.name)
            span.set_data("graphql.field_path", field_path)
            span.set_data("graphql.path", ".".join(map(str, info.path.as_list())))

            return _next(root, info, *args, **kwargs)


def _patch_execute():
    # type: () -> None
    old_execute_async = strawberry_schema.execute
    old_execute_sync = strawberry_schema.execute_sync

    async def _sentry_patched_execute_async(*args, **kwargs):
        # type: (Any, Any) -> ExecutionResult
        hub = Hub.current
        integration = hub.get_integration(StrawberryIntegration)
        if integration is None:
            return await old_execute_async(*args, **kwargs)

        result = await old_execute_async(*args, **kwargs)

        if "execution_context" in kwargs and result.errors:
            with hub.configure_scope() as scope:
                event_processor = _make_request_event_processor(
                    kwargs["execution_context"]
                )
                scope.add_event_processor(event_processor)

        return result

    def _sentry_patched_execute_sync(*args, **kwargs):
        # type: (Any, Any) -> ExecutionResult
        hub = Hub.current
        integration = hub.get_integration(StrawberryIntegration)
        if integration is None:
            return old_execute_sync(*args, **kwargs)

        result = old_execute_sync(*args, **kwargs)

        if "execution_context" in kwargs and result.errors:
            with hub.configure_scope() as scope:
                event_processor = _make_request_event_processor(
                    kwargs["execution_context"]
                )
                scope.add_event_processor(event_processor)

        return result

    strawberry_schema.execute = _sentry_patched_execute_async
    strawberry_schema.execute_sync = _sentry_patched_execute_sync


def _patch_views():
    # type: () -> None
    old_async_view_handle_errors = async_base_view.AsyncBaseHTTPView._handle_errors
    old_sync_view_handle_errors = sync_base_view.SyncBaseHTTPView._handle_errors

    def _sentry_patched_async_view_handle_errors(self, errors, response_data):
        # type: (Any, List[GraphQLError], GraphQLHTTPResponse) -> None
        old_async_view_handle_errors(self, errors, response_data)
        _sentry_patched_handle_errors(self, errors, response_data)

    def _sentry_patched_sync_view_handle_errors(self, errors, response_data):
        # type: (Any, List[GraphQLError], GraphQLHTTPResponse) -> None
        old_sync_view_handle_errors(self, errors, response_data)
        _sentry_patched_handle_errors(self, errors, response_data)

    def _sentry_patched_handle_errors(self, errors, response_data):
        # type: (Any, List[GraphQLError], GraphQLHTTPResponse) -> None
        hub = Hub.current
        integration = hub.get_integration(StrawberryIntegration)
        if integration is None:
            return

        if not errors:
            return

        with hub.configure_scope() as scope:
            event_processor = _make_response_event_processor(response_data)
            scope.add_event_processor(event_processor)

        with capture_internal_exceptions():
            for error in errors:
                event, hint = event_from_exception(
                    error,
                    client_options=hub.client.options if hub.client else None,
                    mechanism={
                        "type": integration.identifier,
                        "handled": False,
                    },
                )
                hub.capture_event(event, hint=hint)

    async_base_view.AsyncBaseHTTPView._handle_errors = (
        _sentry_patched_async_view_handle_errors
    )
    sync_base_view.SyncBaseHTTPView._handle_errors = (
        _sentry_patched_sync_view_handle_errors
    )


def _make_request_event_processor(execution_context):
    # type: (ExecutionContext) -> EventProcessor

    def inner(event, hint):
        # type: (Event, dict[str, Any]) -> Event
        with capture_internal_exceptions():
            if _should_send_default_pii():
                request_data = event.setdefault("request", {})
                request_data["api_target"] = "graphql"

                if not request_data.get("data"):
                    data = {"query": execution_context.query}

                    if execution_context.variables:
                        data["variables"] = execution_context.variables
                    if execution_context.operation_name:
                        data["operationName"] = execution_context.operation_name

                    request_data["data"] = data

            else:
                try:
                    del event["request"]["data"]
                except (KeyError, TypeError):
                    pass

        return event

    return inner


def _make_response_event_processor(response_data):
    # type: (GraphQLHTTPResponse) -> EventProcessor

    def inner(event, hint):
        # type: (Event, dict[str, Any]) -> Event
        with capture_internal_exceptions():
            if _should_send_default_pii():
                contexts = event.setdefault("contexts", {})
                contexts["response"] = {"data": response_data}

        return event

    return inner


def _guess_if_using_async(extensions):
    # type: (List[SchemaExtension]) -> bool
    if StrawberrySentryAsyncExtension in extensions:
        return True
    elif StrawberrySentrySyncExtension in extensions:
        return False

    return bool(
        {"starlette", "starlite", "litestar", "fastapi"} & set(_get_installed_modules())
    )
