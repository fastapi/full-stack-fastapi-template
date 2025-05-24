import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings  # To potentially get service name
from app.core.db import engine  # Assuming engine is in app.core.db


def init_telemetry(app):
    # Set service name, try from settings or default
    service_name = getattr(settings, "OTEL_SERVICE_NAME", "fastapi-application")

    resource = Resource(attributes={"service.name": service_name})

    # Configure OTLP exporter only if endpoint is explicitly set
    # This prevents connection attempts in CI/test environments
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        span_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            # insecure=True # Set to True if your collector is not using TLS. Adjust as needed.
        )
        processor = BatchSpanProcessor(span_exporter)
        provider.add_span_processor(processor)

    # Sets the global default tracer provider
    trace.set_tracer_provider(provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument SQLAlchemy
    # Ensure the engine is already configured/available when this is called.
    SQLAlchemyInstrumentor().instrument(engine=engine)

    # You can get a tracer instance and create spans if needed for custom instrumentation later
    # tracer = trace.get_tracer(__name__)
