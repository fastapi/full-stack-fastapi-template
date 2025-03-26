import sys
from copy import deepcopy
from datetime import timedelta
from os import environ

from sentry_sdk.api import continue_trace
from sentry_sdk.consts import OP
from sentry_sdk.hub import Hub, _should_send_default_pii
from sentry_sdk.tracing import TRANSACTION_SOURCE_COMPONENT
from sentry_sdk.utils import (
    AnnotatedValue,
    capture_internal_exceptions,
    event_from_exception,
    logger,
    TimeoutThread,
)
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations._wsgi_common import _filter_headers
from sentry_sdk._compat import datetime_utcnow, reraise
from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Any
    from typing import TypeVar
    from typing import Callable
    from typing import Optional

    from sentry_sdk._types import EventProcessor, Event, Hint

    F = TypeVar("F", bound=Callable[..., Any])

# Constants
TIMEOUT_WARNING_BUFFER = 1500  # Buffer time required to send timeout warning to Sentry
MILLIS_TO_SECONDS = 1000.0


def _wrap_init_error(init_error):
    # type: (F) -> F
    def sentry_init_error(*args, **kwargs):
        # type: (*Any, **Any) -> Any

        hub = Hub.current
        integration = hub.get_integration(AwsLambdaIntegration)
        if integration is None:
            return init_error(*args, **kwargs)

        # If an integration is there, a client has to be there.
        client = hub.client  # type: Any

        with capture_internal_exceptions():
            with hub.configure_scope() as scope:
                scope.clear_breadcrumbs()

            exc_info = sys.exc_info()
            if exc_info and all(exc_info):
                sentry_event, hint = event_from_exception(
                    exc_info,
                    client_options=client.options,
                    mechanism={"type": "aws_lambda", "handled": False},
                )
                hub.capture_event(sentry_event, hint=hint)

        return init_error(*args, **kwargs)

    return sentry_init_error  # type: ignore


def _wrap_handler(handler):
    # type: (F) -> F
    def sentry_handler(aws_event, aws_context, *args, **kwargs):
        # type: (Any, Any, *Any, **Any) -> Any

        # Per https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html,
        # `event` here is *likely* a dictionary, but also might be a number of
        # other types (str, int, float, None).
        #
        # In some cases, it is a list (if the user is batch-invoking their
        # function, for example), in which case we'll use the first entry as a
        # representative from which to try pulling request data. (Presumably it
        # will be the same for all events in the list, since they're all hitting
        # the lambda in the same request.)

        if isinstance(aws_event, list) and len(aws_event) >= 1:
            request_data = aws_event[0]
            batch_size = len(aws_event)
        else:
            request_data = aws_event
            batch_size = 1

        if not isinstance(request_data, dict):
            # If we're not dealing with a dictionary, we won't be able to get
            # headers, path, http method, etc in any case, so it's fine that
            # this is empty
            request_data = {}

        hub = Hub.current
        integration = hub.get_integration(AwsLambdaIntegration)
        if integration is None:
            return handler(aws_event, aws_context, *args, **kwargs)

        # If an integration is there, a client has to be there.
        client = hub.client  # type: Any
        configured_time = aws_context.get_remaining_time_in_millis()

        with hub.push_scope() as scope:
            timeout_thread = None
            with capture_internal_exceptions():
                scope.clear_breadcrumbs()
                scope.add_event_processor(
                    _make_request_event_processor(
                        request_data, aws_context, configured_time
                    )
                )
                scope.set_tag(
                    "aws_region", aws_context.invoked_function_arn.split(":")[3]
                )
                if batch_size > 1:
                    scope.set_tag("batch_request", True)
                    scope.set_tag("batch_size", batch_size)

                # Starting the Timeout thread only if the configured time is greater than Timeout warning
                # buffer and timeout_warning parameter is set True.
                if (
                    integration.timeout_warning
                    and configured_time > TIMEOUT_WARNING_BUFFER
                ):
                    waiting_time = (
                        configured_time - TIMEOUT_WARNING_BUFFER
                    ) / MILLIS_TO_SECONDS

                    timeout_thread = TimeoutThread(
                        waiting_time,
                        configured_time / MILLIS_TO_SECONDS,
                    )

                    # Starting the thread to raise timeout warning exception
                    timeout_thread.start()

            headers = request_data.get("headers", {})
            # Some AWS Services (ie. EventBridge) set headers as a list
            # or None, so we must ensure it is a dict
            if not isinstance(headers, dict):
                headers = {}

            transaction = continue_trace(
                headers,
                op=OP.FUNCTION_AWS,
                name=aws_context.function_name,
                source=TRANSACTION_SOURCE_COMPONENT,
            )
            with hub.start_transaction(
                transaction,
                custom_sampling_context={
                    "aws_event": aws_event,
                    "aws_context": aws_context,
                },
            ):
                try:
                    return handler(aws_event, aws_context, *args, **kwargs)
                except Exception:
                    exc_info = sys.exc_info()
                    sentry_event, hint = event_from_exception(
                        exc_info,
                        client_options=client.options,
                        mechanism={"type": "aws_lambda", "handled": False},
                    )
                    hub.capture_event(sentry_event, hint=hint)
                    reraise(*exc_info)
                finally:
                    if timeout_thread:
                        timeout_thread.stop()

    return sentry_handler  # type: ignore


def _drain_queue():
    # type: () -> None
    with capture_internal_exceptions():
        hub = Hub.current
        integration = hub.get_integration(AwsLambdaIntegration)
        if integration is not None:
            # Flush out the event queue before AWS kills the
            # process.
            hub.flush()


class AwsLambdaIntegration(Integration):
    identifier = "aws_lambda"

    def __init__(self, timeout_warning=False):
        # type: (bool) -> None
        self.timeout_warning = timeout_warning

    @staticmethod
    def setup_once():
        # type: () -> None

        lambda_bootstrap = get_lambda_bootstrap()
        if not lambda_bootstrap:
            logger.warning(
                "Not running in AWS Lambda environment, "
                "AwsLambdaIntegration disabled (could not find bootstrap module)"
            )
            return

        if not hasattr(lambda_bootstrap, "handle_event_request"):
            logger.warning(
                "Not running in AWS Lambda environment, "
                "AwsLambdaIntegration disabled (could not find handle_event_request)"
            )
            return

        pre_37 = hasattr(lambda_bootstrap, "handle_http_request")  # Python 3.6 or 2.7

        if pre_37:
            old_handle_event_request = lambda_bootstrap.handle_event_request

            def sentry_handle_event_request(request_handler, *args, **kwargs):
                # type: (Any, *Any, **Any) -> Any
                request_handler = _wrap_handler(request_handler)
                return old_handle_event_request(request_handler, *args, **kwargs)

            lambda_bootstrap.handle_event_request = sentry_handle_event_request

            old_handle_http_request = lambda_bootstrap.handle_http_request

            def sentry_handle_http_request(request_handler, *args, **kwargs):
                # type: (Any, *Any, **Any) -> Any
                request_handler = _wrap_handler(request_handler)
                return old_handle_http_request(request_handler, *args, **kwargs)

            lambda_bootstrap.handle_http_request = sentry_handle_http_request

            # Patch to_json to drain the queue. This should work even when the
            # SDK is initialized inside of the handler

            old_to_json = lambda_bootstrap.to_json

            def sentry_to_json(*args, **kwargs):
                # type: (*Any, **Any) -> Any
                _drain_queue()
                return old_to_json(*args, **kwargs)

            lambda_bootstrap.to_json = sentry_to_json
        else:
            lambda_bootstrap.LambdaRuntimeClient.post_init_error = _wrap_init_error(
                lambda_bootstrap.LambdaRuntimeClient.post_init_error
            )

            old_handle_event_request = lambda_bootstrap.handle_event_request

            def sentry_handle_event_request(  # type: ignore
                lambda_runtime_client, request_handler, *args, **kwargs
            ):
                request_handler = _wrap_handler(request_handler)
                return old_handle_event_request(
                    lambda_runtime_client, request_handler, *args, **kwargs
                )

            lambda_bootstrap.handle_event_request = sentry_handle_event_request

            # Patch the runtime client to drain the queue. This should work
            # even when the SDK is initialized inside of the handler

            def _wrap_post_function(f):
                # type: (F) -> F
                def inner(*args, **kwargs):
                    # type: (*Any, **Any) -> Any
                    _drain_queue()
                    return f(*args, **kwargs)

                return inner  # type: ignore

            lambda_bootstrap.LambdaRuntimeClient.post_invocation_result = (
                _wrap_post_function(
                    lambda_bootstrap.LambdaRuntimeClient.post_invocation_result
                )
            )
            lambda_bootstrap.LambdaRuntimeClient.post_invocation_error = (
                _wrap_post_function(
                    lambda_bootstrap.LambdaRuntimeClient.post_invocation_error
                )
            )


def get_lambda_bootstrap():
    # type: () -> Optional[Any]

    # Python 2.7: Everything is in `__main__`.
    #
    # Python 3.7: If the bootstrap module is *already imported*, it is the
    # one we actually want to use (no idea what's in __main__)
    #
    # Python 3.8: bootstrap is also importable, but will be the same file
    # as __main__ imported under a different name:
    #
    #     sys.modules['__main__'].__file__ == sys.modules['bootstrap'].__file__
    #     sys.modules['__main__'] is not sys.modules['bootstrap']
    #
    # Python 3.9: bootstrap is in __main__.awslambdaricmain
    #
    # On container builds using the `aws-lambda-python-runtime-interface-client`
    # (awslamdaric) module, bootstrap is located in sys.modules['__main__'].bootstrap
    #
    # Such a setup would then make all monkeypatches useless.
    if "bootstrap" in sys.modules:
        return sys.modules["bootstrap"]
    elif "__main__" in sys.modules:
        module = sys.modules["__main__"]
        # python3.9 runtime
        if hasattr(module, "awslambdaricmain") and hasattr(
            module.awslambdaricmain, "bootstrap"
        ):
            return module.awslambdaricmain.bootstrap
        elif hasattr(module, "bootstrap"):
            # awslambdaric python module in container builds
            return module.bootstrap

        # python3.8 runtime
        return module
    else:
        return None


def _make_request_event_processor(aws_event, aws_context, configured_timeout):
    # type: (Any, Any, Any) -> EventProcessor
    start_time = datetime_utcnow()

    def event_processor(sentry_event, hint, start_time=start_time):
        # type: (Event, Hint, datetime) -> Optional[Event]
        remaining_time_in_milis = aws_context.get_remaining_time_in_millis()
        exec_duration = configured_timeout - remaining_time_in_milis

        extra = sentry_event.setdefault("extra", {})
        extra["lambda"] = {
            "function_name": aws_context.function_name,
            "function_version": aws_context.function_version,
            "invoked_function_arn": aws_context.invoked_function_arn,
            "aws_request_id": aws_context.aws_request_id,
            "execution_duration_in_millis": exec_duration,
            "remaining_time_in_millis": remaining_time_in_milis,
        }

        extra["cloudwatch logs"] = {
            "url": _get_cloudwatch_logs_url(aws_context, start_time),
            "log_group": aws_context.log_group_name,
            "log_stream": aws_context.log_stream_name,
        }

        request = sentry_event.get("request", {})

        if "httpMethod" in aws_event:
            request["method"] = aws_event["httpMethod"]

        request["url"] = _get_url(aws_event, aws_context)

        if "queryStringParameters" in aws_event:
            request["query_string"] = aws_event["queryStringParameters"]

        if "headers" in aws_event:
            request["headers"] = _filter_headers(aws_event["headers"])

        if _should_send_default_pii():
            user_info = sentry_event.setdefault("user", {})

            identity = aws_event.get("identity")
            if identity is None:
                identity = {}

            id = identity.get("userArn")
            if id is not None:
                user_info.setdefault("id", id)

            ip = identity.get("sourceIp")
            if ip is not None:
                user_info.setdefault("ip_address", ip)

            if "body" in aws_event:
                request["data"] = aws_event.get("body", "")
        else:
            if aws_event.get("body", None):
                # Unfortunately couldn't find a way to get structured body from AWS
                # event. Meaning every body is unstructured to us.
                request["data"] = AnnotatedValue.removed_because_raw_data()

        sentry_event["request"] = deepcopy(request)

        return sentry_event

    return event_processor


def _get_url(aws_event, aws_context):
    # type: (Any, Any) -> str
    path = aws_event.get("path", None)

    headers = aws_event.get("headers")
    if headers is None:
        headers = {}

    host = headers.get("Host", None)
    proto = headers.get("X-Forwarded-Proto", None)
    if proto and host and path:
        return "{}://{}{}".format(proto, host, path)
    return "awslambda:///{}".format(aws_context.function_name)


def _get_cloudwatch_logs_url(aws_context, start_time):
    # type: (Any, datetime) -> str
    """
    Generates a CloudWatchLogs console URL based on the context object

    Arguments:
        aws_context {Any} -- context from lambda handler

    Returns:
        str -- AWS Console URL to logs.
    """
    formatstring = "%Y-%m-%dT%H:%M:%SZ"
    region = environ.get("AWS_REGION", "")

    url = (
        "https://console.{domain}/cloudwatch/home?region={region}"
        "#logEventViewer:group={log_group};stream={log_stream}"
        ";start={start_time};end={end_time}"
    ).format(
        domain="amazonaws.cn" if region.startswith("cn-") else "aws.amazon.com",
        region=region,
        log_group=aws_context.log_group_name,
        log_stream=aws_context.log_stream_name,
        start_time=(start_time - timedelta(seconds=1)).strftime(formatstring),
        end_time=(datetime_utcnow() + timedelta(seconds=2)).strftime(formatstring),
    )

    return url
