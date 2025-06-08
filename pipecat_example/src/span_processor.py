from typing import Optional

from opentelemetry.context.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span
from opentelemetry.sdk.trace.export import SpanProcessor


class PipecatAttributeTransformer(SpanProcessor):
    def on_start(self, span: Span, parent_context: Optional[Context]) -> None:
        pass

    def on_end(self, span: ReadableSpan) -> None:
        if span._attributes is not None:
            input_value = span._attributes.pop("input", None)
            if input_value is not None:
                span._attributes["braintrust.input"] = input_value
            output_value = span._attributes.pop("output", None)
            if output_value is not None:
                span._attributes["braintrust.output"] = output_value

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: Optional[int] = None) -> None:
        pass
