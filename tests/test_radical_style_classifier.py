import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.code_utils.live_show_math_utils import (
    classify_radical_style,
    radical_hard_style_preserved,
)


def test_simple_single_radical_is_not_mixed():
    assert classify_radical_style(r"\sqrt{6}") == "simple_radical"


def test_simplifiable_radical_without_braces_detected():
    assert classify_radical_style(r"\sqrt18") == "simplifiable_radical"


def test_multi_term_radical_addsub_is_mixed():
    expr = r"5\sqrt{7}+4\sqrt{7}-4\sqrt{5}"
    assert classify_radical_style(expr) == "mixed"


def test_radical_with_times_is_mixed():
    expr = r"2\sqrt{11}\times(3\sqrt{45}+2\sqrt{5})"
    assert classify_radical_style(expr) == "mixed"


def test_fraction_times_radical_keeps_fraction_radical():
    expr = r"\frac{3}{5}\times2\sqrt{6}"
    assert classify_radical_style(expr) == "fraction_radical"


def test_pure_radical_division_is_fraction_radical():
    expr = r"\sqrt{35}\div\sqrt{5}"
    assert classify_radical_style(expr) == "fraction_radical"


def test_style_guard_fails_when_simple_input_drift_to_mixed():
    ok, reason = radical_hard_style_preserved(
        "simple_radical",
        classify_radical_style(r"2\sqrt{11}\times(3\sqrt{45}+2\sqrt{5})"),
    )
    assert ok is False
    assert "style drift" in reason
