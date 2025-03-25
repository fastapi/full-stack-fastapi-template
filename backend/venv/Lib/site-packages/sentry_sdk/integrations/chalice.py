import sys

from sentry_sdk._compat import reraise
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration, DidNotEnable
from sentry_sdk.integrations.aws_lambda import _make_request_event_processor
from sentry_sdk.tracing import TRANSACTION_SOURCE_COMPONENT
from sentry_sdk.utils import (
    capture_internal_exceptions,
    event_from_exception,
    parse_version,
)
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk._functools import wraps

import chalice  # type: ignore
from chalice import Chalice, ChaliceViewError
from chalice.app import EventSourceHandler as ChaliceEventSourceHandler  # type: ignore

if TYPE_CHECKING:
    from typing import Any
    from typing import Dict
    from typing import TypeVar
    from typing import Callable

    F = TypeVar("F", bound=Callable[..., Any])

try:
    from chalice import __version__ as CHALICE_VERSION
except ImportError:
    raise DidNotEnable("Chalice is not installed")


class EventSourceHandler(ChaliceEventSourceHandler):  # type: ignore
    def __call__(self, event, context):
        # type: (Any, Any) -> Any
        hub = Hub.current
        client = hub.client  # type: Any

        with hub.push_scope() as scope:
            with capture_internal_exceptions():
                configured_time = context.get_remaining_time_in_millis()
                scope.add_event_processor(
                    _make_request_event_processor(event, context, configured_time)
                )
            try:
                return ChaliceEventSourceHandler.__call__(self, event, context)
            except Exception:
                exc_info = sys.exc_info()
                event, hint = event_from_exception(
                    exc_info,
                    client_options=client.options,
                    mechanism={"type": "chalice", "handled": False},
                )
                hub.capture_event(event, hint=hint)
                hub.flush()
                reraise(*exc_info)


def _get_view_function_response(app, view_function, function_args):
    # type: (Any, F, Any) -> F
    @wraps(view_function)
    def wrapped_view_function(**function_args):
        # type: (**Any) -> Any
        hub = Hub.current
        client = hub.client  # type: Any
        with hub.push_scope() as scope:
            with capture_internal_exceptions():
                configured_time = app.lambda_context.get_remaining_time_in_millis()
                scope.set_transaction_name(
                    app.lambda_context.function_name,
                    source=TRANSACTION_SOURCE_COMPONENT,
                )

                scope.add_event_processor(
                    _make_request_event_processor(
                        app.current_request.to_dict(),
                        app.lambda_context,
                        configured_time,
                    )
                )
            try:
                return view_function(**function_args)
            except Exception as exc:
                if isinstance(exc, ChaliceViewError):
                    raise
                exc_info = sys.exc_info()
                event, hint = event_from_exception(
                    exc_info,
                    client_options=client.options,
                    mechanism={"type": "chalice", "handled": False},
                )
                hub.capture_event(event, hint=hint)
                hub.flush()
                raise

    return wrapped_view_function  # type: ignore


class ChaliceIntegration(Integration):
    identifier = "chalice"

    @staticmethod
    def setup_once():
        # type: () -> None

        version = parse_version(CHALICE_VERSION)

        if version is None:
            raise DidNotEnable("Unparsable Chalice version: {}".format(CHALICE_VERSION))

        if version < (1, 20):
            old_get_view_function_response = Chalice._get_view_function_response
        else:
            from chalice.app import RestAPIEventHandler

            old_get_view_function_response = (
                RestAPIEventHandler._get_view_function_response
            )

        def sentry_event_response(app, view_function, function_args):
            # type: (Any, F, Dict[str, Any]) -> Any
            wrapped_view_function = _get_view_function_response(
                app, view_function, function_args
            )

            return old_get_view_function_response(
                app, wrapped_view_function, function_args
            )

        if version < (1, 20):
            Chalice._get_view_function_response = sentry_event_response
        else:
            RestAPIEventHandler._get_view_function_response = sentry_event_response
        # for everything else (like events)
        chalice.app.EventSourceHandler = EventSourceHandler
