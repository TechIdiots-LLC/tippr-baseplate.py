"""OpenTelemetry spans that inherit attributes from the code around them.

The Thrift server sets the connection's attributes (``ctx.set``) and each
call's span picks them up (``ContextAwareTracer.start_as_current_span``)::

    with ctx.set({SpanAttributes.RPC_SERVICE: "activity"}):
        with ContextAwareTracer(__name__).start_as_current_span("fn"):
            ...

This is the part of Form Energy's formenergy-observability
(https://github.com/Form-Energy/formenergy-observability,
form_observability/context_aware.py) that baseplate used, brought in so
baseplate doesn't need that package (and Dagster, which it requires).

Copyright (c) 2023 Form Energy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import platform
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Optional

from opentelemetry import trace


def _filter_attributes(attributes: dict[str, Any]) -> dict[str, Any]:
    """Without None values, which spans warn about."""
    return {k: v for k, v in attributes.items() if v is not None}


class _ObservabilityContext:
    """Attributes for the spans started in a block of code, per thread
    (per greenlet under gevent). Use the module's ``ctx``."""

    _local = threading.local()

    @property
    def _stack(self) -> list[dict[str, Any]]:
        if not hasattr(self._local, "stack"):
            self._local.stack = [
                {
                    "host.name": platform.node(),
                    "os.type": platform.system().lower(),
                }
            ]
        return self._local.stack

    @property
    def current_ctx(self) -> dict[str, Any]:
        return self._stack[-1]

    @contextmanager
    def set(self, attributes: dict[str, Any], update_current_span: bool = False) -> Iterator[None]:
        """Add `attributes` for the block; the previous ones come back after."""
        filtered = _filter_attributes(attributes)
        self._stack.append({**self.current_ctx, **filtered})
        if update_current_span:
            trace.get_current_span().set_attributes(filtered)
        try:
            yield
        finally:
            self._stack.pop()

    def get(self, key: str, default: Any = None) -> Any:
        return self.current_ctx.get(key, default)


ctx = _ObservabilityContext()


class ContextAwareTracer:
    """Starts spans with the current ``ctx`` attributes."""

    def __init__(self, library_name: str):
        self._tracer = trace.get_tracer(library_name)

    @contextmanager
    def start_as_current_span(
        self, name: str, attributes: Optional[dict[str, Any]] = None, **kwargs: Any
    ) -> Iterator[trace.Span]:
        """A span named `name` with ``ctx``'s attributes and `attributes`,
        which the spans inside it inherit too."""
        attributes = attributes or {}
        span_attributes = {**ctx.current_ctx, **attributes}
        with (
            ctx.set(attributes),
            self._tracer.start_as_current_span(
                name, attributes=_filter_attributes(span_attributes), **kwargs
            ) as span,
        ):
            yield span
