# -*- coding: utf-8 -*-
"""F9 long-division layout analysis (deterministic, no LLM)."""

from core.routes.analysis import analyze_polynomial_long_division_layout
from core.adaptive.judge import judge_answer_with_feedback


def _as_f9_struct(layout: dict) -> dict:
    """Mirror production merge: caller supplies canonical family_id for F9 UI/tutor."""
    return {**layout, "family_id": "F9", "status": "incorrect"}


def test_f9_layout_structure_error_quotient_term_1():
    layout = analyze_polynomial_long_division_layout("x+1;2x+1;3x+2", "x ... 1", "")
    r = _as_f9_struct(layout)
    assert r["family_id"] == "F9"
    assert r["error_mechanism"] == "structure_error"
    assert r["step_focus"] == "quotient_term_1"
    assert r["main_issue"]


def test_f9_layout_operation_error_quotient_term_1():
    layout = analyze_polynomial_long_division_layout("a;b;-2x ... 0", "x ... 0", "")
    r = _as_f9_struct(layout)
    assert r["family_id"] == "F9"
    assert r["error_mechanism"] == "operation_error"
    assert r["step_focus"] == "quotient_term_1"
    assert r["main_issue"]


def test_f9_layout_sign_error_final_remainder():
    layout = analyze_polynomial_long_division_layout("a;b;c;x ... -1", "x ... 1", "")
    r = _as_f9_struct(layout)
    assert r["family_id"] == "F9"
    assert r["error_mechanism"] == "sign_error"
    assert r["step_focus"] == "final_remainder"
    assert r["main_issue"]


def test_f9_layout_notation_error_empty_step():
    layout = analyze_polynomial_long_division_layout("???", "x ... 1", "")
    r = _as_f9_struct(layout)
    assert r["family_id"] == "F9"
    assert r["error_mechanism"] == "notation_error"
    assert r["step_focus"] == ""
    assert r["main_issue"]


def test_f9_text_answer_qr_tolerant_formats():
    """F9 / poly_div_poly_qr: extra QR shapes + symbolic compare (Task 3)."""
    ca = "-2x^2+x-1 ... 4"
    assert judge_answer_with_feedback(
        "-2x^2 + x - 1 ... 4", ca, family_id="F9"
    )["is_correct"] is True
    assert judge_answer_with_feedback(
        "商:-2x^2+x-1,餘:4", ca, family_id="F9"
    )["is_correct"] is True
    assert judge_answer_with_feedback(
        "商=-2x^2+x-1;餘=4", ca, family_id="F9"
    )["is_correct"] is True
    assert judge_answer_with_feedback(
        "商:-2x^2+x-1餘:4", ca, family_id="F9"
    )["is_correct"] is True
    assert judge_answer_with_feedback(
        "-2x^2+x-1,4", ca, family_id="F9"
    )["is_correct"] is True
    r = judge_answer_with_feedback("-2x^2+x-1,4", ca, family_id="F9")
    assert r.get("analysis_source") == "text_answer_qr_parser"
