try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping  # type: ignore[attr-defined]

from importlib import import_module
import os
import uuid
import random
import socket

from sentry_sdk._compat import (
    PY37,
    datetime_utcnow,
    string_types,
    text_type,
    iteritems,
    check_uwsgi_thread_support,
)
from sentry_sdk.utils import (
    capture_internal_exceptions,
    current_stacktrace,
    disable_capture_event,
    format_timestamp,
    get_sdk_name,
    get_type_name,
    get_default_release,
    handle_in_app,
    is_gevent,
    logger,
)
from sentry_sdk.serializer import serialize
from sentry_sdk.tracing import trace, has_tracing_enabled
from sentry_sdk.transport import HttpTransport, make_transport
from sentry_sdk.consts import (
    DEFAULT_MAX_VALUE_LENGTH,
    DEFAULT_OPTIONS,
    INSTRUMENTER,
    VERSION,
    ClientConstructor,
)
from sentry_sdk.integrations import _DEFAULT_INTEGRATIONS, setup_integrations
from sentry_sdk.utils import ContextVar
from sentry_sdk.sessions import SessionFlusher
from sentry_sdk.envelope import Envelope
from sentry_sdk.profiler import has_profiling_enabled, Profile, setup_profiler
from sentry_sdk.scrubber import EventScrubber
from sentry_sdk.monitor import Monitor
from sentry_sdk.spotlight import setup_spotlight

from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import Optional
    from typing import Sequence
    from typing import Type
    from typing import Union

    from sentry_sdk.integrations import Integration
    from sentry_sdk.scope import Scope
    from sentry_sdk._types import Event, Hint
    from sentry_sdk.session import Session


_client_init_debug = ContextVar("client_init_debug")


SDK_INFO = {
    "name": "sentry.python",  # SDK name will be overridden after integrations have been loaded with sentry_sdk.integrations.setup_integrations()
    "version": VERSION,
    "packages": [{"name": "pypi:sentry-sdk", "version": VERSION}],
}


def _get_options(*args, **kwargs):
    # type: (*Optional[str], **Any) -> Dict[str, Any]
    if args and (isinstance(args[0], (text_type, bytes, str)) or args[0] is None):
        dsn = args[0]  # type: Optional[str]
        args = args[1:]
    else:
        dsn = None

    if len(args) > 1:
        raise TypeError("Only single positional argument is expected")

    rv = dict(DEFAULT_OPTIONS)
    options = dict(*args, **kwargs)
    if dsn is not None and options.get("dsn") is None:
        options["dsn"] = dsn

    for key, value in iteritems(options):
        if key not in rv:
            # Option "with_locals" was renamed to "include_local_variables"
            if key == "with_locals":
                msg = (
                    "Deprecated: The option 'with_locals' was renamed to 'include_local_variables'. "
                    "Please use 'include_local_variables'. The option 'with_locals' will be removed in the future."
                )
                logger.warning(msg)
                rv["include_local_variables"] = value
                continue

            # Option "request_bodies" was renamed to "max_request_body_size"
            if key == "request_bodies":
                msg = (
                    "Deprecated: The option 'request_bodies' was renamed to 'max_request_body_size'. "
                    "Please use 'max_request_body_size'. The option 'request_bodies' will be removed in the future."
                )
                logger.warning(msg)
                rv["max_request_body_size"] = value
                continue

            raise TypeError("Unknown option %r" % (key,))

        rv[key] = value

    if rv["dsn"] is None:
        rv["dsn"] = os.environ.get("SENTRY_DSN")

    if rv["release"] is None:
        rv["release"] = get_default_release()

    if rv["environment"] is None:
        rv["environment"] = os.environ.get("SENTRY_ENVIRONMENT") or "production"

    if rv["debug"] is None:
        rv["debug"] = os.environ.get("SENTRY_DEBUG", "False").lower() in (
            "true",
            "1",
            "t",
        )

    if rv["server_name"] is None and hasattr(socket, "gethostname"):
        rv["server_name"] = socket.gethostname()

    if rv["instrumenter"] is None:
        rv["instrumenter"] = INSTRUMENTER.SENTRY

    if rv["project_root"] is None:
        try:
            project_root = os.getcwd()
        except Exception:
            project_root = None

        rv["project_root"] = project_root

    if rv["enable_tracing"] is True and rv["traces_sample_rate"] is None:
        rv["traces_sample_rate"] = 1.0

    if rv["event_scrubber"] is None:
        rv["event_scrubber"] = EventScrubber()

    if rv["socket_options"] and not isinstance(rv["socket_options"], list):
        logger.warning(
            "Ignoring socket_options because of unexpected format. See urllib3.HTTPConnection.socket_options for the expected format."
        )
        rv["socket_options"] = None

    return rv


try:
    # Python 3.6+
    module_not_found_error = ModuleNotFoundError
except Exception:
    # Older Python versions
    module_not_found_error = ImportError  # type: ignore


class _Client(object):
    """The client is internally responsible for capturing the events and
    forwarding them to sentry through the configured transport.  It takes
    the client options as keyword arguments and optionally the DSN as first
    argument.

    Alias of :py:class:`Client`. (Was created for better intelisense support)
    """

    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        self.options = get_options(*args, **kwargs)  # type: Dict[str, Any]

        self._init_impl()

    def __getstate__(self):
        # type: () -> Any
        return {"options": self.options}

    def __setstate__(self, state):
        # type: (Any) -> None
        self.options = state["options"]
        self._init_impl()

    def _setup_instrumentation(self, functions_to_trace):
        # type: (Sequence[Dict[str, str]]) -> None
        """
        Instruments the functions given in the list `functions_to_trace` with the `@sentry_sdk.tracing.trace` decorator.
        """
        for function in functions_to_trace:
            class_name = None
            function_qualname = function["qualified_name"]
            module_name, function_name = function_qualname.rsplit(".", 1)

            try:
                # Try to import module and function
                # ex: "mymodule.submodule.funcname"

                module_obj = import_module(module_name)
                function_obj = getattr(module_obj, function_name)
                setattr(module_obj, function_name, trace(function_obj))
                logger.debug("Enabled tracing for %s", function_qualname)

            except module_not_found_error:
                try:
                    # Try to import a class
                    # ex: "mymodule.submodule.MyClassName.member_function"

                    module_name, class_name = module_name.rsplit(".", 1)
                    module_obj = import_module(module_name)
                    class_obj = getattr(module_obj, class_name)
                    function_obj = getattr(class_obj, function_name)
                    function_type = type(class_obj.__dict__[function_name])
                    traced_function = trace(function_obj)

                    if function_type in (staticmethod, classmethod):
                        traced_function = staticmethod(traced_function)

                    setattr(class_obj, function_name, traced_function)
                    setattr(module_obj, class_name, class_obj)
                    logger.debug("Enabled tracing for %s", function_qualname)

                except Exception as e:
                    logger.warning(
                        "Can not enable tracing for '%s'. (%s) Please check your `functions_to_trace` parameter.",
                        function_qualname,
                        e,
                    )

            except Exception as e:
                logger.warning(
                    "Can not enable tracing for '%s'. (%s) Please check your `functions_to_trace` parameter.",
                    function_qualname,
                    e,
                )

    def _init_impl(self):
        # type: () -> None
        old_debug = _client_init_debug.get(False)

        def _capture_envelope(envelope):
            # type: (Envelope) -> None
            if self.transport is not None:
                self.transport.capture_envelope(envelope)

        try:
            _client_init_debug.set(self.options["debug"])
            self.transport = make_transport(self.options)

            self.monitor = None
            if self.transport:
                if self.options["enable_backpressure_handling"]:
                    self.monitor = Monitor(self.transport)

            self.session_flusher = SessionFlusher(capture_func=_capture_envelope)

            self.metrics_aggregator = None  # type: Optional[MetricsAggregator]
            experiments = self.options.get("_experiments", {})
            if experiments.get("enable_metrics", True):
                # Context vars are not working correctly on Python <=3.6
                # with gevent.
                metrics_supported = not is_gevent() or PY37
                if metrics_supported:
                    from sentry_sdk.metrics import MetricsAggregator

                    self.metrics_aggregator = MetricsAggregator(
                        capture_func=_capture_envelope,
                        enable_code_locations=bool(
                            experiments.get("metric_code_locations", True)
                        ),
                    )
                else:
                    logger.info(
                        "Metrics not supported on Python 3.6 and lower with gevent."
                    )

            max_request_body_size = ("always", "never", "small", "medium")
            if self.options["max_request_body_size"] not in max_request_body_size:
                raise ValueError(
                    "Invalid value for max_request_body_size. Must be one of {}".format(
                        max_request_body_size
                    )
                )

            if self.options["_experiments"].get("otel_powered_performance", False):
                logger.debug(
                    "[OTel] Enabling experimental OTel-powered performance monitoring."
                )
                self.options["instrumenter"] = INSTRUMENTER.OTEL
                _DEFAULT_INTEGRATIONS.append(
                    "sentry_sdk.integrations.opentelemetry.integration.OpenTelemetryIntegration",
                )

            self.integrations = setup_integrations(
                self.options["integrations"],
                with_defaults=self.options["default_integrations"],
                with_auto_enabling_integrations=self.options[
                    "auto_enabling_integrations"
                ],
            )

            self.spotlight = None
            if self.options.get("spotlight"):
                self.spotlight = setup_spotlight(self.options)

            sdk_name = get_sdk_name(list(self.integrations.keys()))
            SDK_INFO["name"] = sdk_name
            logger.debug("Setting SDK name to '%s'", sdk_name)

            if has_profiling_enabled(self.options):
                try:
                    setup_profiler(self.options)
                except Exception as e:
                    logger.debug("Can not set up profiler. (%s)", e)

        finally:
            _client_init_debug.set(old_debug)

        self._setup_instrumentation(self.options.get("functions_to_trace", []))

        if (
            self.monitor
            or self.metrics_aggregator
            or has_profiling_enabled(self.options)
            or isinstance(self.transport, HttpTransport)
        ):
            # If we have anything on that could spawn a background thread, we
            # need to check if it's safe to use them.
            check_uwsgi_thread_support()

    @property
    def dsn(self):
        # type: () -> Optional[str]
        """Returns the configured DSN as string."""
        return self.options["dsn"]

    def _prepare_event(
        self,
        event,  # type: Event
        hint,  # type: Hint
        scope,  # type: Optional[Scope]
    ):
        # type: (...) -> Optional[Event]

        if event.get("timestamp") is None:
            event["timestamp"] = datetime_utcnow()

        if scope is not None:
            is_transaction = event.get("type") == "transaction"
            event_ = scope.apply_to_event(event, hint, self.options)

            # one of the event/error processors returned None
            if event_ is None:
                if self.transport:
                    self.transport.record_lost_event(
                        "event_processor",
                        data_category=("transaction" if is_transaction else "error"),
                    )
                return None

            event = event_

        if (
            self.options["attach_stacktrace"]
            and "exception" not in event
            and "stacktrace" not in event
            and "threads" not in event
        ):
            with capture_internal_exceptions():
                event["threads"] = {
                    "values": [
                        {
                            "stacktrace": current_stacktrace(
                                include_local_variables=self.options.get(
                                    "include_local_variables", True
                                ),
                                max_value_length=self.options.get(
                                    "max_value_length", DEFAULT_MAX_VALUE_LENGTH
                                ),
                            ),
                            "crashed": False,
                            "current": True,
                        }
                    ]
                }

        for key in "release", "environment", "server_name", "dist":
            if event.get(key) is None and self.options[key] is not None:
                event[key] = text_type(self.options[key]).strip()  # type: ignore[literal-required]
        if event.get("sdk") is None:
            sdk_info = dict(SDK_INFO)
            sdk_info["integrations"] = sorted(self.integrations.keys())
            event["sdk"] = sdk_info

        if event.get("platform") is None:
            event["platform"] = "python"

        event = handle_in_app(
            event,
            self.options["in_app_exclude"],
            self.options["in_app_include"],
            self.options["project_root"],
        )

        if event is not None:
            event_scrubber = self.options["event_scrubber"]
            if event_scrubber and not self.options["send_default_pii"]:
                event_scrubber.scrub_event(event)

        # Postprocess the event here so that annotated types do
        # generally not surface in before_send
        if event is not None:
            event = serialize(
                event,
                max_request_body_size=self.options.get("max_request_body_size"),
                max_value_length=self.options.get("max_value_length"),
            )

        before_send = self.options["before_send"]
        if (
            before_send is not None
            and event is not None
            and event.get("type") != "transaction"
        ):
            new_event = None
            with capture_internal_exceptions():
                new_event = before_send(event, hint or {})
            if new_event is None:
                logger.info("before send dropped event")
                if self.transport:
                    self.transport.record_lost_event(
                        "before_send", data_category="error"
                    )
            event = new_event  # type: ignore

        before_send_transaction = self.options["before_send_transaction"]
        if (
            before_send_transaction is not None
            and event is not None
            and event.get("type") == "transaction"
        ):
            new_event = None
            with capture_internal_exceptions():
                new_event = before_send_transaction(event, hint or {})
            if new_event is None:
                logger.info("before send transaction dropped event")
                if self.transport:
                    self.transport.record_lost_event(
                        "before_send", data_category="transaction"
                    )
            event = new_event  # type: ignore

        return event

    def _is_ignored_error(self, event, hint):
        # type: (Event, Hint) -> bool
        exc_info = hint.get("exc_info")
        if exc_info is None:
            return False

        error = exc_info[0]
        error_type_name = get_type_name(exc_info[0])
        error_full_name = "%s.%s" % (exc_info[0].__module__, error_type_name)

        for ignored_error in self.options["ignore_errors"]:
            # String types are matched against the type name in the
            # exception only
            if isinstance(ignored_error, string_types):
                if ignored_error == error_full_name or ignored_error == error_type_name:
                    return True
            else:
                if issubclass(error, ignored_error):
                    return True

        return False

    def _should_capture(
        self,
        event,  # type: Event
        hint,  # type: Hint
        scope=None,  # type: Optional[Scope]
    ):
        # type: (...) -> bool
        # Transactions are sampled independent of error events.
        is_transaction = event.get("type") == "transaction"
        if is_transaction:
            return True

        ignoring_prevents_recursion = scope is not None and not scope._should_capture
        if ignoring_prevents_recursion:
            return False

        ignored_by_config_option = self._is_ignored_error(event, hint)
        if ignored_by_config_option:
            return False

        return True

    def _should_sample_error(
        self,
        event,  # type: Event
        hint,  # type: Hint
    ):
        # type: (...) -> bool
        error_sampler = self.options.get("error_sampler", None)

        if callable(error_sampler):
            with capture_internal_exceptions():
                sample_rate = error_sampler(event, hint)
        else:
            sample_rate = self.options["sample_rate"]

        try:
            not_in_sample_rate = sample_rate < 1.0 and random.random() >= sample_rate
        except NameError:
            logger.warning(
                "The provided error_sampler raised an error. Defaulting to sampling the event."
            )

            # If the error_sampler raised an error, we should sample the event, since the default behavior
            # (when no sample_rate or error_sampler is provided) is to sample all events.
            not_in_sample_rate = False
        except TypeError:
            parameter, verb = (
                ("error_sampler", "returned")
                if callable(error_sampler)
                else ("sample_rate", "contains")
            )
            logger.warning(
                "The provided %s %s an invalid value of %s. The value should be a float or a bool. Defaulting to sampling the event."
                % (parameter, verb, repr(sample_rate))
            )

            # If the sample_rate has an invalid value, we should sample the event, since the default behavior
            # (when no sample_rate or error_sampler is provided) is to sample all events.
            not_in_sample_rate = False

        if not_in_sample_rate:
            # because we will not sample this event, record a "lost event".
            if self.transport:
                self.transport.record_lost_event("sample_rate", data_category="error")

            return False

        return True

    def _update_session_from_event(
        self,
        session,  # type: Session
        event,  # type: Event
    ):
        # type: (...) -> None

        crashed = False
        errored = False
        user_agent = None

        exceptions = (event.get("exception") or {}).get("values")
        if exceptions:
            errored = True
            for error in exceptions:
                mechanism = error.get("mechanism")
                if isinstance(mechanism, Mapping) and mechanism.get("handled") is False:
                    crashed = True
                    break

        user = event.get("user")

        if session.user_agent is None:
            headers = (event.get("request") or {}).get("headers")
            for k, v in iteritems(headers or {}):
                if k.lower() == "user-agent":
                    user_agent = v
                    break

        session.update(
            status="crashed" if crashed else None,
            user=user,
            user_agent=user_agent,
            errors=session.errors + (errored or crashed),
        )

    def capture_event(
        self,
        event,  # type: Event
        hint=None,  # type: Optional[Hint]
        scope=None,  # type: Optional[Scope]
    ):
        # type: (...) -> Optional[str]
        """Captures an event.

        :param event: A ready-made event that can be directly sent to Sentry.

        :param hint: Contains metadata about the event that can be read from `before_send`, such as the original exception object or a HTTP request object.

        :param scope: An optional :py:class:`sentry_sdk.Scope` to apply to events.
            The `scope` and `scope_kwargs` parameters are mutually exclusive.

        :returns: An event ID. May be `None` if there is no DSN set or of if the SDK decided to discard the event for other reasons. In such situations setting `debug=True` on `init()` may help.
        """
        if disable_capture_event.get(False):
            return None

        if hint is None:
            hint = {}
        event_id = event.get("event_id")
        hint = dict(hint or ())  # type: Hint

        if event_id is None:
            event["event_id"] = event_id = uuid.uuid4().hex
        if not self._should_capture(event, hint, scope):
            return None

        profile = event.pop("profile", None)

        event_opt = self._prepare_event(event, hint, scope)
        if event_opt is None:
            return None

        # whenever we capture an event we also check if the session needs
        # to be updated based on that information.
        session = scope._session if scope else None
        if session:
            self._update_session_from_event(session, event)

        is_transaction = event_opt.get("type") == "transaction"
        is_checkin = event_opt.get("type") == "check_in"

        if (
            not is_transaction
            and not is_checkin
            and not self._should_sample_error(event, hint)
        ):
            return None

        tracing_enabled = has_tracing_enabled(self.options)
        attachments = hint.get("attachments")

        trace_context = event_opt.get("contexts", {}).get("trace") or {}
        dynamic_sampling_context = trace_context.pop("dynamic_sampling_context", {})

        # If tracing is enabled all events should go to /envelope endpoint.
        # If no tracing is enabled only transactions, events with attachments, and checkins should go to the /envelope endpoint.
        should_use_envelope_endpoint = (
            tracing_enabled
            or is_transaction
            or is_checkin
            or bool(attachments)
            or bool(self.spotlight)
        )
        if should_use_envelope_endpoint:
            headers = {
                "event_id": event_opt["event_id"],
                "sent_at": format_timestamp(datetime_utcnow()),
            }  # type: dict[str, object]

            if dynamic_sampling_context:
                headers["trace"] = dynamic_sampling_context

            envelope = Envelope(headers=headers)

            if is_transaction:
                if isinstance(profile, Profile):
                    envelope.add_profile(profile.to_json(event_opt, self.options))
                envelope.add_transaction(event_opt)
            elif is_checkin:
                envelope.add_checkin(event_opt)
            else:
                envelope.add_event(event_opt)

            for attachment in attachments or ():
                envelope.add_item(attachment.to_envelope_item())

            if self.spotlight:
                self.spotlight.capture_envelope(envelope)

            if self.transport is None:
                return None

            self.transport.capture_envelope(envelope)

        else:
            if self.transport is None:
                return None

            # All other events go to the legacy /store/ endpoint (will be removed in the future).
            self.transport.capture_event(event_opt)

        return event_id

    def capture_session(
        self, session  # type: Session
    ):
        # type: (...) -> None
        if not session.release:
            logger.info("Discarded session update because of missing release")
        else:
            self.session_flusher.add_session(session)

    def get_integration(
        self, name_or_class  # type: Union[str, Type[Integration]]
    ):
        # type: (...) -> Any
        """Returns the integration for this client by name or class.
        If the client does not have that integration then `None` is returned.
        """
        if isinstance(name_or_class, str):
            integration_name = name_or_class
        elif name_or_class.identifier is not None:
            integration_name = name_or_class.identifier
        else:
            raise ValueError("Integration has no name")

        return self.integrations.get(integration_name)

    def close(
        self,
        timeout=None,  # type: Optional[float]
        callback=None,  # type: Optional[Callable[[int, float], None]]
    ):
        # type: (...) -> None
        """
        Close the client and shut down the transport. Arguments have the same
        semantics as :py:meth:`Client.flush`.
        """
        if self.transport is not None:
            self.flush(timeout=timeout, callback=callback)
            self.session_flusher.kill()
            if self.metrics_aggregator is not None:
                self.metrics_aggregator.kill()
            if self.monitor:
                self.monitor.kill()
            self.transport.kill()
            self.transport = None

    def flush(
        self,
        timeout=None,  # type: Optional[float]
        callback=None,  # type: Optional[Callable[[int, float], None]]
    ):
        # type: (...) -> None
        """
        Wait for the current events to be sent.

        :param timeout: Wait for at most `timeout` seconds. If no `timeout` is provided, the `shutdown_timeout` option value is used.

        :param callback: Is invoked with the number of pending events and the configured timeout.
        """
        if self.transport is not None:
            if timeout is None:
                timeout = self.options["shutdown_timeout"]
            self.session_flusher.flush()
            if self.metrics_aggregator is not None:
                self.metrics_aggregator.flush()
            self.transport.flush(timeout=timeout, callback=callback)

    def __enter__(self):
        # type: () -> _Client
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # type: (Any, Any, Any) -> None
        self.close()


from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    # Make mypy, PyCharm and other static analyzers think `get_options` is a
    # type to have nicer autocompletion for params.
    #
    # Use `ClientConstructor` to define the argument types of `init` and
    # `Dict[str, Any]` to tell static analyzers about the return type.

    class get_options(ClientConstructor, Dict[str, Any]):  # noqa: N801
        pass

    class Client(ClientConstructor, _Client):
        pass

else:
    # Alias `get_options` for actual usage. Go through the lambda indirection
    # to throw PyCharm off of the weakly typed signature (it would otherwise
    # discover both the weakly typed signature of `_init` and our faked `init`
    # type).

    get_options = (lambda: _get_options)()
    Client = (lambda: _Client)()
