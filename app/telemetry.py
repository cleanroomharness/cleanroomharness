"""OpenTelemetry setup.

Instruments FastAPI when OTEL_ENABLED=true. Traces should carry request ID,
tenant ID, model name, tool name, policy decision, latency, and error state —
never raw secrets or sensitive payloads.
"""

import logging

from fastapi import FastAPI

from app.settings import get_settings

logger = logging.getLogger("cleanroom.telemetry")


def setup_telemetry(app: FastAPI) -> None:
    settings = get_settings()
    if not settings.otel_enabled:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    except ImportError:
        logger.warning("OTEL_ENABLED is true but opentelemetry packages are missing")
        return

    resource = Resource.create({"service.name": settings.app_name})
    provider = TracerProvider(resource=resource)

    if settings.otel_exporter_otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
                )
            )
        except ImportError:
            logger.warning("OTLP endpoint set but exporter package missing; using console")
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    else:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
