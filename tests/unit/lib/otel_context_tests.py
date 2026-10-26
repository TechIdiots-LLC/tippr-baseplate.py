from opentelemetry.test.test_base import TestBase

from baseplate.lib.otel_context import ContextAwareTracer, ctx


class OtelContextTests(TestBase):
    def test_ctx_set_and_restore(self):
        assert ctx.get("rpc.service") is None
        with ctx.set({"rpc.service": "activity", "skipped": None}):
            assert ctx.get("rpc.service") == "activity"
            assert "skipped" not in ctx.current_ctx
            with ctx.set({"rpc.service": "other"}):
                assert ctx.get("rpc.service") == "other"
            assert ctx.get("rpc.service") == "activity"
        assert ctx.get("rpc.service") is None
        assert "host.name" in ctx.current_ctx
        assert "os.type" in ctx.current_ctx

    def test_spans_inherit_ctx_attributes(self):
        tracer = ContextAwareTracer(__name__)
        with ctx.set({"rpc.service": "activity"}):
            with tracer.start_as_current_span("outer", attributes={"rpc.method": "count"}):
                with tracer.start_as_current_span("inner"):
                    pass
        spans = {span.name: span for span in self.get_finished_spans()}
        assert spans["outer"].attributes["rpc.service"] == "activity"
        assert spans["outer"].attributes["rpc.method"] == "count"
        assert "host.name" in spans["outer"].attributes
        # attributes given to a span are inherited by the spans inside it
        assert spans["inner"].attributes["rpc.method"] == "count"
        assert spans["inner"].parent.span_id == spans["outer"].context.span_id
