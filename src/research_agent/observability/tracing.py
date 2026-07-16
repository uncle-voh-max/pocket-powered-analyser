from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

tracer: trace.Tracer | None = None


def setup_tracing(service_name: str = "research-agent") -> None:
    global tracer
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = ConsoleSpanExporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(service_name)


def get_tracer() -> trace.Tracer:
    global tracer
    if tracer is None:
        setup_tracing()
    return tracer or trace.get_tracer("research-agent")
