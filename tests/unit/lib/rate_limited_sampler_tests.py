from opentelemetry.sdk.trace.sampling import ALWAYS_OFF, ALWAYS_ON, Decision

from baseplate.lib.tracing import RateLimited


def test_samples_up_to_the_rate_then_drops_without_waiting():
    sampler = RateLimited(ALWAYS_ON, 3)
    decisions = [sampler.should_sample(None, 1, "span").decision for _ in range(5)]
    assert decisions == [Decision.RECORD_AND_SAMPLE] * 3 + [Decision.DROP] * 2


def test_keeps_the_parent_samplers_drop():
    sampler = RateLimited(ALWAYS_OFF, 3)
    assert sampler.should_sample(None, 1, "span").decision == Decision.DROP
