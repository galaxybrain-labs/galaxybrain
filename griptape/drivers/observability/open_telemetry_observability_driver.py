from attrs import define, Factory, field
from griptape.common import Observable
from griptape.drivers import BaseObservabilityDriver
from opentelemetry import trace
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.trace import Tracer, Status, StatusCode
from types import TracebackType
from typing import Any, Optional


@define
class OpenTelemetryObservabilityDriver(BaseObservabilityDriver):
    service_name: str = field(kw_only=True)
    span_processor: SpanProcessor = field(kw_only=True)
    trace_provider: TracerProvider = field(
        default=Factory(
            lambda self: TracerProvider(resource=Resource(attributes={"service.name": self.service_name})),
            takes_self=True,
        ),
        kw_only=True,
    )
    _tracer: Optional[Tracer] = None
    _root_span_context_manager: Any = None

    def __attrs_post_init__(self):
        self.trace_provider.add_span_processor(self.span_processor)
        self._tracer = trace.get_tracer(self.service_name, tracer_provider=self.trace_provider)

    def __enter__(self) -> None:
        ThreadingInstrumentor().instrument()
        self._root_span_context_manager = self._tracer.start_as_current_span("main")  # pyright: ignore[reportCallIssue]
        self._root_span_context_manager.__enter__()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> bool:
        root_span = trace.get_current_span()
        if exc_value:
            root_span = trace.get_current_span()
            root_span.set_status(Status(StatusCode.ERROR))
            root_span.record_exception(exc_value)
        else:
            root_span.set_status(Status(StatusCode.OK))
        if self._root_span_context_manager:
            self._root_span_context_manager.__exit__(exc_type, exc_value, exc_traceback)
            self._root_span_context_manager = None
        self.trace_provider.force_flush()
        ThreadingInstrumentor().uninstrument()
        return False

    def observe(self, call: Observable.Call) -> Any:
        func = call.func
        instance = call.instance

        class_name = f"{instance.__class__.__name__}." if instance else ""
        span_name = f"{class_name}{func.__name__}()"
        with self._tracer.start_as_current_span(span_name) as span:  # pyright: ignore[reportCallIssue]
            try:
                result = call()
                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise e