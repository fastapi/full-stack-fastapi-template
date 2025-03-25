from opentelemetry.context import (  # type: ignore
    create_key,
)

SENTRY_TRACE_KEY = create_key("sentry-trace")
SENTRY_BAGGAGE_KEY = create_key("sentry-baggage")
