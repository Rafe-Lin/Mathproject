# -*- coding: utf-8 -*-
"""Deterministic F9 tutor fallback (no LLM)."""

from core.routes.analysis import _tutor_deterministic_fallback, _tutor_guidance_is_compliant


def test_f9_fallback_structure_quotient_term_1_copy():
    sa = {
        "family_id": "F9",
        "error_mechanism": "structure_error",
        "step_focus": "quotient_term_1",
        "main_issue": "長除法各列的對齊與次序關係不清楚，請先釐清商、乘回、相減三種列。",
        "status": "incorrect",
    }
    g = _tutor_deterministic_fallback(sa)
    assert "對齊商與被除式" in g["hint_focus"]
    assert "第一次商" in g["guided_question"]
    assert "先寫" in g["micro_step"]


def test_f9_fallback_sign_error_final_remainder_copy():
    sa = {
        "family_id": "poly_div_poly_qr",
        "error_mechanism": "sign_error",
        "step_focus": "final_remainder",
        "main_issue": "相減時整行變號有誤，請逐項檢查正負。",
        "status": "incorrect",
    }
    g = _tutor_deterministic_fallback(sa)
    assert "餘項" in g["hint_focus"] or "變號" in g["hint_focus"]
    assert len(g["hint_focus"]) <= 18
    assert len(g["guided_question"]) <= 28
    assert len(g["micro_step"]) <= 22


def test_f9_fallback_length_limits_all_rows():
    for mech, step in [
        ("structure_error", "subtract_row_1"),
        ("operation_error", "quotient_term_1"),
        ("notation_error", ""),
    ]:
        sa = {
            "family_id": "F9",
            "error_mechanism": mech,
            "step_focus": step,
            "main_issue": "長除法各列的對齊與次序關係不清楚，請先釐清商、乘回、相減三種列。",
            "status": "incorrect",
        }
        g = _tutor_deterministic_fallback(sa)
        assert len(g["hint_focus"]) <= 18
        assert len(g["guided_question"]) <= 28
        assert len(g["micro_step"]) <= 22


def test_deterministic_fallback_passes_compliance_gate():
    sa = {
        "family_id": "F9",
        "error_mechanism": "notation_error",
        "step_focus": "",
        "main_issue": "長除法書寫不完整，請補齊商與餘數的標示。",
        "status": "incorrect",
    }
    g = _tutor_deterministic_fallback(sa)
    assert _tutor_guidance_is_compliant(g, sa) is True
