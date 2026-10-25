from logpilot.data.synth import SIGNALS, generate_split
from logpilot.data.taxonomy import CATEGORIES


def test_every_category_has_signals_for_both_halves():
    for cat in CATEGORIES:
        assert len(SIGNALS[cat]) >= 2, cat  # need even + odd variants


def test_splits_are_balanced_and_labelled():
    cases = generate_split("test", per_category=3)
    assert len(cases) == 3 * len(CATEGORIES)
    assert {c.root_cause for c in cases} == set(CATEGORIES)


def test_generation_is_deterministic():
    a = [c.log for c in generate_split("dev", 2)]
    b = [c.log for c in generate_split("dev", 2)]
    assert a == b


def test_signal_lines_appear_in_log():
    for c in generate_split("dev", 2):
        for line in c.signal_lines:
            assert line in c.log


def test_no_exact_signal_leakage_between_incidents_and_test():
    incident_signals = {line for c in generate_split("incidents", 8) for line in c.signal_lines}
    test_signals = {line for c in generate_split("test", 10) for line in c.signal_lines}
    assert not incident_signals & test_signals


def test_only_incidents_carry_resolutions():
    assert all(c.resolution for c in generate_split("incidents", 1))
    assert not any(c.resolution for c in generate_split("test", 1))
