from time import time

from opentelemetry.context import get_value  # type: ignore
from opentelemetry.sdk.trace import SpanProcessor  # type: ignore
from opentelemetry.semconv.trace import SpanAttributes  # type: ignore
from opentelemetry.trace import (  # type: ignore
    format_span_id,
    format_trace_id,
    get_current_span,
    SpanContext,
    Span as OTelSpan,
    SpanKind,
)
from opentelemetry.trace.span import (  # type: ignore
    INVALID_SPAN_ID,
    INVALID_TRACE_ID,
)
from sentry_sdk._compat import utc_from_timestamp
from sentry_sdk.consts import INSTRUMENTER
from sentry_sdk.hub import Hub
from sentry_sdk.integrations.opentelemetry.consts import (
    SENTRY_BAGGAGE_KEY,
    SENTRY_TRACE_KEY,
)
from sentry_sdk.scope import add_global_event_processor
from sentry_sdk.tracing import Transaction, Span as SentrySpan
from sentry_sdk.utils import Dsn
from sentry_sdk._types import TYPE_CHECKING

from urllib3.util import parse_url as urlparse

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union

    from sentry_sdk._types import Event, Hint

OPEN_TELEMETRY_CONTEXT = "otel"
SPAN_MAX_TIME_OPEN_MINUTES = 10


def link_trace_context_to_error_event(event, otel_span_map):
    # type: (Event, Dict[str, Union[Transaction, SentrySpan]]) -> Event
    hub = Hub.current
    if not hub:
        return event

    if hub.client and hub.client.options["instrumenter"] != INSTRUMENTER.OTEL:
        return event

    if hasattr(event, "type") and event["type"] == "transaction":
        return event

    otel_span = get_current_span()
    if not otel_span:
        return event

    ctx = otel_span.get_span_context()
    trace_id = format_trace_id(ctx.trace_id)
    span_id = format_span_id(ctx.span_id)

    if trace_id == INVALID_TRACE_ID or span_id == INVALID_SPAN_ID:
        return event

    sentry_span = otel_span_map.get(span_id, None)
    if not sentry_span:
        return event

    contexts = event.setdefault("contexts", {})
    contexts.setdefault("trace", {}).update(sentry_span.get_trace_context())

    return event


class SentrySpanProcessor(SpanProcessor):  # type: ignore
    """
    Converts OTel spans into Sentry spans so they can be sent to the Sentry backend.
    """

    # The mapping from otel span ids to sentry spans
    otel_span_map = {}  # type: Dict[str, Union[Transaction, SentrySpan]]

    # The currently open spans. Elements will be discarded after SPAN_MAX_TIME_OPEN_MINUTES
    open_spans = {}  # type: dict[int, set[str]]

    def __new__(cls):
        # type: () -> SentrySpanProcessor
        if not hasattr(cls, "instance"):
            cls.instance = super(SentrySpanProcessor, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        # type: () -> None
        @add_global_event_processor
        def global_event_processor(event, hint):
            # type: (Event, Hint) -> Event
            return link_trace_context_to_error_event(event, self.otel_span_map)

    def _prune_old_spans(self):
        # type: (SentrySpanProcessor) -> None
        """
        Prune spans that have been open for too long.
        """
        current_time_minutes = int(time() / 60)
        for span_start_minutes in list(
            self.open_spans.keys()
        ):  # making a list because we change the dict
            # prune empty open spans buckets
            if self.open_spans[span_start_minutes] == set():
                self.open_spans.pop(span_start_minutes)

            # prune old buckets
            elif current_time_minutes - span_start_minutes > SPAN_MAX_TIME_OPEN_MINUTES:
                for span_id in self.open_spans.pop(span_start_minutes):
                    self.otel_span_map.pop(span_id, None)

    def on_start(self, otel_span, parent_context=None):
        # type: (OTelSpan, Optional[SpanContext]) -> None
        hub = Hub.current
        if not hub:
            return

        if not hub.client or (hub.client and not hub.client.dsn):
            return

        try:
            _ = Dsn(hub.client.dsn or "")
        except Exception:
            return

        if hub.client and hub.client.options["instrumenter"] != INSTRUMENTER.OTEL:
            return

        if not otel_span.get_span_context().is_valid:
            return

        if self._is_sentry_span(hub, otel_span):
            return

        trace_data = self._get_trace_data(otel_span, parent_context)

        parent_span_id = trace_data["parent_span_id"]
        sentry_parent_span = (
            self.otel_span_map.get(parent_span_id, None) if parent_span_id else None
        )

        sentry_span = None
        if sentry_parent_span:
            sentry_span = sentry_parent_span.start_child(
                span_id=trace_data["span_id"],
                description=otel_span.name,
                start_timestamp=utc_from_timestamp(
                    otel_span.start_time / 1e9
                ),  # OTel spans have nanosecond precision
                instrumenter=INSTRUMENTER.OTEL,
            )
        else:
            sentry_span = hub.start_transaction(
                name=otel_span.name,
                span_id=trace_data["span_id"],
                parent_span_id=parent_span_id,
                trace_id=trace_data["trace_id"],
                baggage=trace_data["baggage"],
                start_timestamp=utc_from_timestamp(
                    otel_span.start_time / 1e9
                ),  # OTel spans have nanosecond precision
                instrumenter=INSTRUMENTER.OTEL,
            )

        self.otel_span_map[trace_data["span_id"]] = sentry_span

        span_start_in_minutes = int(
            otel_span.start_time / 1e9 / 60
        )  # OTel spans have nanosecond precision
        self.open_spans.setdefault(span_start_in_minutes, set()).add(
            trace_data["span_id"]
        )
        self._prune_old_spans()

    def on_end(self, otel_span):
        # type: (OTelSpan) -> None
        hub = Hub.current
        if not hub:
            return

        if hub.client and hub.client.options["instrumenter"] != INSTRUMENTER.OTEL:
            return

        span_context = otel_span.get_span_context()
        if not span_context.is_valid:
            return

        span_id = format_span_id(span_context.span_id)
        sentry_span = self.otel_span_map.pop(span_id, None)
        if not sentry_span:
            return

        sentry_span.op = otel_span.name

        self._update_span_with_otel_status(sentry_span, otel_span)

        if isinstance(sentry_span, Transaction):
            sentry_span.name = otel_span.name
            sentry_span.set_context(
                OPEN_TELEMETRY_CONTEXT, self._get_otel_context(otel_span)
            )
            self._update_transaction_with_otel_data(sentry_span, otel_span)

        else:
            self._update_span_with_otel_data(sentry_span, otel_span)

        sentry_span.finish(
            end_timestamp=utc_from_timestamp(otel_span.end_time / 1e9)
        )  # OTel spans have nanosecond precision

        span_start_in_minutes = int(
            otel_span.start_time / 1e9 / 60
        )  # OTel spans have nanosecond precision
        self.open_spans.setdefault(span_start_in_minutes, set()).discard(span_id)
        self._prune_old_spans()

    def _is_sentry_span(self, hub, otel_span):
        # type: (Hub, OTelSpan) -> bool
        """
        Break infinite loop:
        HTTP requests to Sentry are caught by OTel and send again to Sentry.
        """
        otel_span_url = otel_span.attributes.get(SpanAttributes.HTTP_URL, None)
        dsn_url = hub.client and Dsn(hub.client.dsn or "").netloc

        if otel_span_url and dsn_url in otel_span_url:
            return True

        return False

    def _get_otel_context(self, otel_span):
        # type: (OTelSpan) -> Dict[str, Any]
        """
        Returns the OTel context for Sentry.
        See: https://develop.sentry.dev/sdk/performance/opentelemetry/#step-5-add-opentelemetry-context
        """
        ctx = {}

        if otel_span.attributes:
            ctx["attributes"] = dict(otel_span.attributes)

        if otel_span.resource.attributes:
            ctx["resource"] = dict(otel_span.resource.attributes)

        return ctx

    def _get_trace_data(self, otel_span, parent_context):
        # type: (OTelSpan, SpanContext) -> Dict[str, Any]
        """
        Extracts tracing information from one OTel span and its parent OTel context.
        """
        trace_data = {}
        span_context = otel_span.get_span_context()

        span_id = format_span_id(span_context.span_id)
        trace_data["span_id"] = span_id

        trace_id = format_trace_id(span_context.trace_id)
        trace_data["trace_id"] = trace_id

        parent_span_id = (
            format_span_id(otel_span.parent.span_id) if otel_span.parent else None
        )
        trace_data["parent_span_id"] = parent_span_id

        sentry_trace_data = get_value(SENTRY_TRACE_KEY, parent_context)
        trace_data["parent_sampled"] = (
            sentry_trace_data["parent_sampled"] if sentry_trace_data else None
        )

        baggage = get_value(SENTRY_BAGGAGE_KEY, parent_context)
        trace_data["baggage"] = baggage

        return trace_data

    def _update_span_with_otel_status(self, sentry_span, otel_span):
        # type: (SentrySpan, OTelSpan) -> None
        """
        Set the Sentry span status from the OTel span
        """
        if otel_span.status.is_unset:
            return

        if otel_span.status.is_ok:
            sentry_span.set_status("ok")
            return

        sentry_span.set_status("internal_error")

    def _update_span_with_otel_data(self, sentry_span, otel_span):
        # type: (SentrySpan, OTelSpan) -> None
        """
        Convert OTel span data and update the Sentry span with it.
        This should eventually happen on the server when ingesting the spans.
        """
        for key, val in otel_span.attributes.items():
            sentry_span.set_data(key, val)

        sentry_span.set_data("otel.kind", otel_span.kind)

        op = otel_span.name
        description = otel_span.name

        http_method = otel_span.attributes.get(SpanAttributes.HTTP_METHOD, None)
        db_query = otel_span.attributes.get(SpanAttributes.DB_SYSTEM, None)

        if http_method:
            op = "http"

            if otel_span.kind == SpanKind.SERVER:
                op += ".server"
            elif otel_span.kind == SpanKind.CLIENT:
                op += ".client"

            description = http_method

            peer_name = otel_span.attributes.get(SpanAttributes.NET_PEER_NAME, None)
            if peer_name:
                description += " {}".format(peer_name)

            target = otel_span.attributes.get(SpanAttributes.HTTP_TARGET, None)
            if target:
                description += " {}".format(target)

            if not peer_name and not target:
                url = otel_span.attributes.get(SpanAttributes.HTTP_URL, None)
                if url:
                    parsed_url = urlparse(url)
                    url = "{}://{}{}".format(
                        parsed_url.scheme, parsed_url.netloc, parsed_url.path
                    )
                    description += " {}".format(url)

            status_code = otel_span.attributes.get(
                SpanAttributes.HTTP_STATUS_CODE, None
            )
            if status_code:
                sentry_span.set_http_status(status_code)

        elif db_query:
            op = "db"
            statement = otel_span.attributes.get(SpanAttributes.DB_STATEMENT, None)
            if statement:
                description = statement

        sentry_span.op = op
        sentry_span.description = description

    def _update_transaction_with_otel_data(self, sentry_span, otel_span):
        # type: (SentrySpan, OTelSpan) -> None
        http_method = otel_span.attributes.get(SpanAttributes.HTTP_METHOD)

        if http_method:
            status_code = otel_span.attributes.get(SpanAttributes.HTTP_STATUS_CODE)
            if status_code:
                sentry_span.set_http_status(status_code)

            op = "http"

            if otel_span.kind == SpanKind.SERVER:
                op += ".server"
            elif otel_span.kind == SpanKind.CLIENT:
                op += ".client"

            sentry_span.op = op
