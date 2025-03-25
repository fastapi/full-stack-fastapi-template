from __future__ import absolute_import

import weakref
from sentry_sdk.consts import OP

from sentry_sdk.api import continue_trace
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import DidNotEnable, Integration
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.tracing import TRANSACTION_SOURCE_TASK
from sentry_sdk.utils import (
    capture_internal_exceptions,
    event_from_exception,
    format_timestamp,
    parse_version,
)

try:
    from rq.queue import Queue
    from rq.timeouts import JobTimeoutException
    from rq.version import VERSION as RQ_VERSION
    from rq.worker import Worker
    from rq.job import JobStatus
except ImportError:
    raise DidNotEnable("RQ not installed")

from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable

    from sentry_sdk._types import Event, EventProcessor
    from sentry_sdk.utils import ExcInfo

    from rq.job import Job


class RqIntegration(Integration):
    identifier = "rq"

    @staticmethod
    def setup_once():
        # type: () -> None

        version = parse_version(RQ_VERSION)

        if version is None:
            raise DidNotEnable("Unparsable RQ version: {}".format(RQ_VERSION))

        if version < (0, 6):
            raise DidNotEnable("RQ 0.6 or newer is required.")

        old_perform_job = Worker.perform_job

        def sentry_patched_perform_job(self, job, *args, **kwargs):
            # type: (Any, Job, *Queue, **Any) -> bool
            hub = Hub.current
            integration = hub.get_integration(RqIntegration)

            if integration is None:
                return old_perform_job(self, job, *args, **kwargs)

            client = hub.client
            assert client is not None

            with hub.push_scope() as scope:
                scope.clear_breadcrumbs()
                scope.add_event_processor(_make_event_processor(weakref.ref(job)))

                transaction = continue_trace(
                    job.meta.get("_sentry_trace_headers") or {},
                    op=OP.QUEUE_TASK_RQ,
                    name="unknown RQ task",
                    source=TRANSACTION_SOURCE_TASK,
                )

                with capture_internal_exceptions():
                    transaction.name = job.func_name

                with hub.start_transaction(
                    transaction, custom_sampling_context={"rq_job": job}
                ):
                    rv = old_perform_job(self, job, *args, **kwargs)

            if self.is_horse:
                # We're inside of a forked process and RQ is
                # about to call `os._exit`. Make sure that our
                # events get sent out.
                client.flush()

            return rv

        Worker.perform_job = sentry_patched_perform_job

        old_handle_exception = Worker.handle_exception

        def sentry_patched_handle_exception(self, job, *exc_info, **kwargs):
            # type: (Worker, Any, *Any, **Any) -> Any
            # Note, the order of the `or` here is important,
            # because calling `job.is_failed` will change `_status`.
            if job._status == JobStatus.FAILED or job.is_failed:
                _capture_exception(exc_info)

            return old_handle_exception(self, job, *exc_info, **kwargs)

        Worker.handle_exception = sentry_patched_handle_exception

        old_enqueue_job = Queue.enqueue_job

        def sentry_patched_enqueue_job(self, job, **kwargs):
            # type: (Queue, Any, **Any) -> Any
            hub = Hub.current
            if hub.get_integration(RqIntegration) is not None:
                if hub.scope.span is not None:
                    job.meta["_sentry_trace_headers"] = dict(
                        hub.iter_trace_propagation_headers()
                    )

            return old_enqueue_job(self, job, **kwargs)

        Queue.enqueue_job = sentry_patched_enqueue_job

        ignore_logger("rq.worker")


def _make_event_processor(weak_job):
    # type: (Callable[[], Job]) -> EventProcessor
    def event_processor(event, hint):
        # type: (Event, dict[str, Any]) -> Event
        job = weak_job()
        if job is not None:
            with capture_internal_exceptions():
                extra = event.setdefault("extra", {})
                rq_job = {
                    "job_id": job.id,
                    "func": job.func_name,
                    "args": job.args,
                    "kwargs": job.kwargs,
                    "description": job.description,
                }

                if job.enqueued_at:
                    rq_job["enqueued_at"] = format_timestamp(job.enqueued_at)
                if job.started_at:
                    rq_job["started_at"] = format_timestamp(job.started_at)

                extra["rq-job"] = rq_job

        if "exc_info" in hint:
            with capture_internal_exceptions():
                if issubclass(hint["exc_info"][0], JobTimeoutException):
                    event["fingerprint"] = ["rq", "JobTimeoutException", job.func_name]

        return event

    return event_processor


def _capture_exception(exc_info, **kwargs):
    # type: (ExcInfo, **Any) -> None
    hub = Hub.current
    if hub.get_integration(RqIntegration) is None:
        return

    # If an integration is there, a client has to be there.
    client = hub.client  # type: Any

    event, hint = event_from_exception(
        exc_info,
        client_options=client.options,
        mechanism={"type": "rq", "handled": False},
    )

    hub.capture_event(event, hint=hint)
