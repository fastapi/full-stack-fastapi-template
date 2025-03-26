from __future__ import absolute_import

import sys
import time

try:
    from typing import cast
except ImportError:
    cast = lambda _, o: o

from sentry_sdk.api import continue_trace
from sentry_sdk.consts import OP
from sentry_sdk._compat import reraise
from sentry_sdk._functools import wraps
from sentry_sdk.crons import capture_checkin, MonitorStatus
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration, DidNotEnable
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.tracing import BAGGAGE_HEADER_NAME, TRANSACTION_SOURCE_TASK
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.utils import (
    capture_internal_exceptions,
    event_from_exception,
    logger,
    match_regex_list,
)

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import List
    from typing import Optional
    from typing import Tuple
    from typing import TypeVar
    from typing import Union

    from sentry_sdk.tracing import Span
    from sentry_sdk._types import (
        EventProcessor,
        Event,
        Hint,
        ExcInfo,
        MonitorConfig,
        MonitorConfigScheduleType,
        MonitorConfigScheduleUnit,
    )

    F = TypeVar("F", bound=Callable[..., Any])


try:
    from celery import VERSION as CELERY_VERSION  # type: ignore
    from celery import Task, Celery
    from celery.app.trace import task_has_custom
    from celery.beat import Scheduler  # type: ignore
    from celery.exceptions import (  # type: ignore
        Ignore,
        Reject,
        Retry,
        SoftTimeLimitExceeded,
    )
    from celery.schedules import crontab, schedule  # type: ignore
    from celery.signals import (  # type: ignore
        task_failure,
        task_success,
        task_retry,
    )
except ImportError:
    raise DidNotEnable("Celery not installed")

try:
    from redbeat.schedulers import RedBeatScheduler  # type: ignore
except ImportError:
    RedBeatScheduler = None


CELERY_CONTROL_FLOW_EXCEPTIONS = (Retry, Ignore, Reject)


class CeleryIntegration(Integration):
    identifier = "celery"

    def __init__(
        self,
        propagate_traces=True,
        monitor_beat_tasks=False,
        exclude_beat_tasks=None,
    ):
        # type: (bool, bool, Optional[List[str]]) -> None
        self.propagate_traces = propagate_traces
        self.monitor_beat_tasks = monitor_beat_tasks
        self.exclude_beat_tasks = exclude_beat_tasks

        if monitor_beat_tasks:
            _patch_beat_apply_entry()
            _patch_redbeat_maybe_due()
            _setup_celery_beat_signals()

    @staticmethod
    def setup_once():
        # type: () -> None
        if CELERY_VERSION < (3,):
            raise DidNotEnable("Celery 3 or newer required.")

        import celery.app.trace as trace  # type: ignore

        old_build_tracer = trace.build_tracer

        def sentry_build_tracer(name, task, *args, **kwargs):
            # type: (Any, Any, *Any, **Any) -> Any
            if not getattr(task, "_sentry_is_patched", False):
                # determine whether Celery will use __call__ or run and patch
                # accordingly
                if task_has_custom(task, "__call__"):
                    type(task).__call__ = _wrap_task_call(task, type(task).__call__)
                else:
                    task.run = _wrap_task_call(task, task.run)

                # `build_tracer` is apparently called for every task
                # invocation. Can't wrap every celery task for every invocation
                # or we will get infinitely nested wrapper functions.
                task._sentry_is_patched = True

            return _wrap_tracer(task, old_build_tracer(name, task, *args, **kwargs))

        trace.build_tracer = sentry_build_tracer

        from celery.app.task import Task  # type: ignore

        Task.apply_async = _wrap_apply_async(Task.apply_async)

        _patch_worker_exit()

        # This logger logs every status of every task that ran on the worker.
        # Meaning that every task's breadcrumbs are full of stuff like "Task
        # <foo> raised unexpected <bar>".
        ignore_logger("celery.worker.job")
        ignore_logger("celery.app.trace")

        # This is stdout/err redirected to a logger, can't deal with this
        # (need event_level=logging.WARN to reproduce)
        ignore_logger("celery.redirected")


def _now_seconds_since_epoch():
    # type: () -> float
    # We cannot use `time.perf_counter()` when dealing with the duration
    # of a Celery task, because the start of a Celery task and
    # the end are recorded in different processes.
    # Start happens in the Celery Beat process,
    # the end in a Celery Worker process.
    return time.time()


class NoOpMgr:
    def __enter__(self):
        # type: () -> None
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        # type: (Any, Any, Any) -> None
        return None


def _wrap_apply_async(f):
    # type: (F) -> F
    @wraps(f)
    def apply_async(*args, **kwargs):
        # type: (*Any, **Any) -> Any
        hub = Hub.current
        integration = hub.get_integration(CeleryIntegration)

        if integration is None:
            return f(*args, **kwargs)

        # Note: kwargs can contain headers=None, so no setdefault!
        # Unsure which backend though.
        kwarg_headers = kwargs.get("headers") or {}
        propagate_traces = kwarg_headers.pop(
            "sentry-propagate-traces", integration.propagate_traces
        )

        if not propagate_traces:
            return f(*args, **kwargs)

        try:
            task_started_from_beat = args[1][0] == "BEAT"
        except (IndexError, TypeError):
            task_started_from_beat = False

        task = args[0]

        span_mgr = (
            hub.start_span(op=OP.QUEUE_SUBMIT_CELERY, description=task.name)
            if not task_started_from_beat
            else NoOpMgr()
        )  # type: Union[Span, NoOpMgr]

        with span_mgr as span:
            with capture_internal_exceptions():
                headers = (
                    dict(hub.iter_trace_propagation_headers(span))
                    if span is not None
                    else {}
                )
                if integration.monitor_beat_tasks:
                    headers.update(
                        {
                            "sentry-monitor-start-timestamp-s": "%.9f"
                            % _now_seconds_since_epoch(),
                        }
                    )

                if headers:
                    existing_baggage = kwarg_headers.get(BAGGAGE_HEADER_NAME)
                    sentry_baggage = headers.get(BAGGAGE_HEADER_NAME)

                    combined_baggage = sentry_baggage or existing_baggage
                    if sentry_baggage and existing_baggage:
                        combined_baggage = "{},{}".format(
                            existing_baggage,
                            sentry_baggage,
                        )

                    kwarg_headers.update(headers)
                    if combined_baggage:
                        kwarg_headers[BAGGAGE_HEADER_NAME] = combined_baggage

                    # https://github.com/celery/celery/issues/4875
                    #
                    # Need to setdefault the inner headers too since other
                    # tracing tools (dd-trace-py) also employ this exact
                    # workaround and we don't want to break them.
                    kwarg_headers.setdefault("headers", {}).update(headers)
                    if combined_baggage:
                        kwarg_headers["headers"][BAGGAGE_HEADER_NAME] = combined_baggage

                    # Add the Sentry options potentially added in `sentry_apply_entry`
                    # to the headers (done when auto-instrumenting Celery Beat tasks)
                    for key, value in kwarg_headers.items():
                        if key.startswith("sentry-"):
                            kwarg_headers["headers"][key] = value

                    kwargs["headers"] = kwarg_headers

            return f(*args, **kwargs)

    return apply_async  # type: ignore


def _wrap_tracer(task, f):
    # type: (Any, F) -> F

    # Need to wrap tracer for pushing the scope before prerun is sent, and
    # popping it after postrun is sent.
    #
    # This is the reason we don't use signals for hooking in the first place.
    # Also because in Celery 3, signal dispatch returns early if one handler
    # crashes.
    @wraps(f)
    def _inner(*args, **kwargs):
        # type: (*Any, **Any) -> Any
        hub = Hub.current
        if hub.get_integration(CeleryIntegration) is None:
            return f(*args, **kwargs)

        with hub.push_scope() as scope:
            scope._name = "celery"
            scope.clear_breadcrumbs()
            scope.add_event_processor(_make_event_processor(task, *args, **kwargs))

            transaction = None

            # Celery task objects are not a thing to be trusted. Even
            # something such as attribute access can fail.
            with capture_internal_exceptions():
                transaction = continue_trace(
                    args[3].get("headers") or {},
                    op=OP.QUEUE_TASK_CELERY,
                    name="unknown celery task",
                    source=TRANSACTION_SOURCE_TASK,
                )
                transaction.name = task.name
                transaction.set_status("ok")

            if transaction is None:
                return f(*args, **kwargs)

            with hub.start_transaction(
                transaction,
                custom_sampling_context={
                    "celery_job": {
                        "task": task.name,
                        # for some reason, args[1] is a list if non-empty but a
                        # tuple if empty
                        "args": list(args[1]),
                        "kwargs": args[2],
                    }
                },
            ):
                return f(*args, **kwargs)

    return _inner  # type: ignore


def _wrap_task_call(task, f):
    # type: (Any, F) -> F

    # Need to wrap task call because the exception is caught before we get to
    # see it. Also celery's reported stacktrace is untrustworthy.

    # functools.wraps is important here because celery-once looks at this
    # method's name.
    # https://github.com/getsentry/sentry-python/issues/421
    @wraps(f)
    def _inner(*args, **kwargs):
        # type: (*Any, **Any) -> Any
        try:
            return f(*args, **kwargs)
        except Exception:
            exc_info = sys.exc_info()
            with capture_internal_exceptions():
                _capture_exception(task, exc_info)
            reraise(*exc_info)

    return _inner  # type: ignore


def _make_event_processor(task, uuid, args, kwargs, request=None):
    # type: (Any, Any, Any, Any, Optional[Any]) -> EventProcessor
    def event_processor(event, hint):
        # type: (Event, Hint) -> Optional[Event]

        with capture_internal_exceptions():
            tags = event.setdefault("tags", {})
            tags["celery_task_id"] = uuid
            extra = event.setdefault("extra", {})
            extra["celery-job"] = {
                "task_name": task.name,
                "args": args,
                "kwargs": kwargs,
            }

        if "exc_info" in hint:
            with capture_internal_exceptions():
                if issubclass(hint["exc_info"][0], SoftTimeLimitExceeded):
                    event["fingerprint"] = [
                        "celery",
                        "SoftTimeLimitExceeded",
                        getattr(task, "name", task),
                    ]

        return event

    return event_processor


def _capture_exception(task, exc_info):
    # type: (Any, ExcInfo) -> None
    hub = Hub.current

    if hub.get_integration(CeleryIntegration) is None:
        return
    if isinstance(exc_info[1], CELERY_CONTROL_FLOW_EXCEPTIONS):
        # ??? Doesn't map to anything
        _set_status(hub, "aborted")
        return

    _set_status(hub, "internal_error")

    if hasattr(task, "throws") and isinstance(exc_info[1], task.throws):
        return

    # If an integration is there, a client has to be there.
    client = hub.client  # type: Any

    event, hint = event_from_exception(
        exc_info,
        client_options=client.options,
        mechanism={"type": "celery", "handled": False},
    )

    hub.capture_event(event, hint=hint)


def _set_status(hub, status):
    # type: (Hub, str) -> None
    with capture_internal_exceptions():
        with hub.configure_scope() as scope:
            if scope.span is not None:
                scope.span.set_status(status)


def _patch_worker_exit():
    # type: () -> None

    # Need to flush queue before worker shutdown because a crashing worker will
    # call os._exit
    from billiard.pool import Worker  # type: ignore

    old_workloop = Worker.workloop

    def sentry_workloop(*args, **kwargs):
        # type: (*Any, **Any) -> Any
        try:
            return old_workloop(*args, **kwargs)
        finally:
            with capture_internal_exceptions():
                hub = Hub.current
                if hub.get_integration(CeleryIntegration) is not None:
                    hub.flush()

    Worker.workloop = sentry_workloop


def _get_headers(task):
    # type: (Task) -> Dict[str, Any]
    headers = task.request.get("headers") or {}

    # flatten nested headers
    if "headers" in headers:
        headers.update(headers["headers"])
        del headers["headers"]

    headers.update(task.request.get("properties") or {})

    return headers


def _get_humanized_interval(seconds):
    # type: (float) -> Tuple[int, MonitorConfigScheduleUnit]
    TIME_UNITS = (  # noqa: N806
        ("day", 60 * 60 * 24.0),
        ("hour", 60 * 60.0),
        ("minute", 60.0),
    )

    seconds = float(seconds)
    for unit, divider in TIME_UNITS:
        if seconds >= divider:
            interval = int(seconds / divider)
            return (interval, cast("MonitorConfigScheduleUnit", unit))

    return (int(seconds), "second")


def _get_monitor_config(celery_schedule, app, monitor_name):
    # type: (Any, Celery, str) -> MonitorConfig
    monitor_config = {}  # type: MonitorConfig
    schedule_type = None  # type: Optional[MonitorConfigScheduleType]
    schedule_value = None  # type: Optional[Union[str, int]]
    schedule_unit = None  # type: Optional[MonitorConfigScheduleUnit]

    if isinstance(celery_schedule, crontab):
        schedule_type = "crontab"
        schedule_value = (
            "{0._orig_minute} "
            "{0._orig_hour} "
            "{0._orig_day_of_month} "
            "{0._orig_month_of_year} "
            "{0._orig_day_of_week}".format(celery_schedule)
        )
    elif isinstance(celery_schedule, schedule):
        schedule_type = "interval"
        (schedule_value, schedule_unit) = _get_humanized_interval(
            celery_schedule.seconds
        )

        if schedule_unit == "second":
            logger.warning(
                "Intervals shorter than one minute are not supported by Sentry Crons. Monitor '%s' has an interval of %s seconds. Use the `exclude_beat_tasks` option in the celery integration to exclude it.",
                monitor_name,
                schedule_value,
            )
            return {}

    else:
        logger.warning(
            "Celery schedule type '%s' not supported by Sentry Crons.",
            type(celery_schedule),
        )
        return {}

    monitor_config["schedule"] = {}
    monitor_config["schedule"]["type"] = schedule_type
    monitor_config["schedule"]["value"] = schedule_value

    if schedule_unit is not None:
        monitor_config["schedule"]["unit"] = schedule_unit

    monitor_config["timezone"] = (
        (
            hasattr(celery_schedule, "tz")
            and celery_schedule.tz is not None
            and str(celery_schedule.tz)
        )
        or app.timezone
        or "UTC"
    )

    return monitor_config


def _patch_beat_apply_entry():
    # type: () -> None
    original_apply_entry = Scheduler.apply_entry

    def sentry_apply_entry(*args, **kwargs):
        # type: (*Any, **Any) -> None
        scheduler, schedule_entry = args
        app = scheduler.app

        celery_schedule = schedule_entry.schedule
        monitor_name = schedule_entry.name

        hub = Hub.current
        integration = hub.get_integration(CeleryIntegration)
        if integration is None:
            return original_apply_entry(*args, **kwargs)

        if match_regex_list(monitor_name, integration.exclude_beat_tasks):
            return original_apply_entry(*args, **kwargs)

        with hub.configure_scope() as scope:
            # When tasks are started from Celery Beat, make sure each task has its own trace.
            scope.set_new_propagation_context()

            monitor_config = _get_monitor_config(celery_schedule, app, monitor_name)

            is_supported_schedule = bool(monitor_config)
            if is_supported_schedule:
                headers = schedule_entry.options.pop("headers", {})
                headers.update(
                    {
                        "sentry-monitor-slug": monitor_name,
                        "sentry-monitor-config": monitor_config,
                    }
                )

                check_in_id = capture_checkin(
                    monitor_slug=monitor_name,
                    monitor_config=monitor_config,
                    status=MonitorStatus.IN_PROGRESS,
                )
                headers.update({"sentry-monitor-check-in-id": check_in_id})

                # Set the Sentry configuration in the options of the ScheduleEntry.
                # Those will be picked up in `apply_async` and added to the headers.
                schedule_entry.options["headers"] = headers

            return original_apply_entry(*args, **kwargs)

    Scheduler.apply_entry = sentry_apply_entry


def _patch_redbeat_maybe_due():
    # type: () -> None

    if RedBeatScheduler is None:
        return

    original_maybe_due = RedBeatScheduler.maybe_due

    def sentry_maybe_due(*args, **kwargs):
        # type: (*Any, **Any) -> None
        scheduler, schedule_entry = args
        app = scheduler.app

        celery_schedule = schedule_entry.schedule
        monitor_name = schedule_entry.name

        hub = Hub.current
        integration = hub.get_integration(CeleryIntegration)
        if integration is None:
            return original_maybe_due(*args, **kwargs)

        if match_regex_list(monitor_name, integration.exclude_beat_tasks):
            return original_maybe_due(*args, **kwargs)

        with hub.configure_scope() as scope:
            # When tasks are started from Celery Beat, make sure each task has its own trace.
            scope.set_new_propagation_context()

            monitor_config = _get_monitor_config(celery_schedule, app, monitor_name)

            is_supported_schedule = bool(monitor_config)
            if is_supported_schedule:
                headers = schedule_entry.options.pop("headers", {})
                headers.update(
                    {
                        "sentry-monitor-slug": monitor_name,
                        "sentry-monitor-config": monitor_config,
                    }
                )

                check_in_id = capture_checkin(
                    monitor_slug=monitor_name,
                    monitor_config=monitor_config,
                    status=MonitorStatus.IN_PROGRESS,
                )
                headers.update({"sentry-monitor-check-in-id": check_in_id})

                # Set the Sentry configuration in the options of the ScheduleEntry.
                # Those will be picked up in `apply_async` and added to the headers.
                schedule_entry.options["headers"] = headers

            return original_maybe_due(*args, **kwargs)

    RedBeatScheduler.maybe_due = sentry_maybe_due


def _setup_celery_beat_signals():
    # type: () -> None
    task_success.connect(crons_task_success)
    task_failure.connect(crons_task_failure)
    task_retry.connect(crons_task_retry)


def crons_task_success(sender, **kwargs):
    # type: (Task, Dict[Any, Any]) -> None
    logger.debug("celery_task_success %s", sender)
    headers = _get_headers(sender)

    if "sentry-monitor-slug" not in headers:
        return

    monitor_config = headers.get("sentry-monitor-config", {})

    start_timestamp_s = float(headers["sentry-monitor-start-timestamp-s"])

    capture_checkin(
        monitor_slug=headers["sentry-monitor-slug"],
        monitor_config=monitor_config,
        check_in_id=headers["sentry-monitor-check-in-id"],
        duration=_now_seconds_since_epoch() - start_timestamp_s,
        status=MonitorStatus.OK,
    )


def crons_task_failure(sender, **kwargs):
    # type: (Task, Dict[Any, Any]) -> None
    logger.debug("celery_task_failure %s", sender)
    headers = _get_headers(sender)

    if "sentry-monitor-slug" not in headers:
        return

    monitor_config = headers.get("sentry-monitor-config", {})

    start_timestamp_s = float(headers["sentry-monitor-start-timestamp-s"])

    capture_checkin(
        monitor_slug=headers["sentry-monitor-slug"],
        monitor_config=monitor_config,
        check_in_id=headers["sentry-monitor-check-in-id"],
        duration=_now_seconds_since_epoch() - start_timestamp_s,
        status=MonitorStatus.ERROR,
    )


def crons_task_retry(sender, **kwargs):
    # type: (Task, Dict[Any, Any]) -> None
    logger.debug("celery_task_retry %s", sender)
    headers = _get_headers(sender)

    if "sentry-monitor-slug" not in headers:
        return

    monitor_config = headers.get("sentry-monitor-config", {})

    start_timestamp_s = float(headers["sentry-monitor-start-timestamp-s"])

    capture_checkin(
        monitor_slug=headers["sentry-monitor-slug"],
        monitor_config=monitor_config,
        check_in_id=headers["sentry-monitor-check-in-id"],
        duration=_now_seconds_since_epoch() - start_timestamp_s,
        status=MonitorStatus.ERROR,
    )
