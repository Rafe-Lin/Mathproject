# -*- coding: utf-8 -*-
"""Rule-only refinement when handwriting inference would be unknown (F1/F2/F11)."""

from core.routes.analysis import (
    _handwriting_structured_analysis,
    _refine_polynomial_unknown_mechanism,
)


def test_f1_constant_expected_but_x_remains_with_cancellable_terms():
    r = _refine_polynomial_unknown_mechanism(
        "F1",
        recognized_expression="12x+10",
        final_expression="12x+10",
        expected_answer="10",
        question_text="6x + 1 - 6x + 9",
    )
    assert r is not None
    assert r["error_mechanism"] == "combine_error"
    assert r["step_focus"] == "like_terms"


def test_f2_sign_error_unflipped_negative_parenthesis():
    r = _refine_polynomial_unknown_mechanism(
        "F2",
        recognized_expression="x-1",
        final_expression="x-1",
        expected_answer="1-x",
        question_text="-(x-1)",
    )
    assert r is not None
    assert r["error_mechanism"] == "sign_error"
    assert r["step_focus"] == "sign_distribution"


def test_f2_structure_error_missing_degree_after_brackets():
    r = _refine_polynomial_unknown_mechanism(
        "poly_add_sub_nested",
        recognized_expression="2x+1",
        final_expression="2x+1",
        expected_answer="x**2+2*x+1",
        question_text="化簡 (x+1)^2",
    )
    assert r is not None
    assert r["error_mechanism"] == "structure_error"
    assert r["step_focus"] == "bracket_scope"


def test_f11_combine_error_same_terms_wrong_coefficients():
    r = _refine_polynomial_unknown_mechanism(
        "poly_mixed_simplify",
        recognized_expression="x**2+x+1",
        final_expression="x**2+x+1",
        expected_answer="x**2+2*x+1",
        question_text="(x+1)**2 展開並化簡",
    )
    assert r is not None
    assert r["error_mechanism"] == "combine_error"
    assert r["step_focus"] == "simplify_combine"


def test_f11_structure_error_missing_term_with_bracket_question():
    r = _refine_polynomial_unknown_mechanism(
        "F11",
        recognized_expression="2*x+1",
        final_expression="2*x+1",
        expected_answer="x**2+2*x+1",
        question_text="展開 (x+1)^2",
    )
    assert r is not None
    assert r["error_mechanism"] == "structure_error"
    assert r["step_focus"] == "expansion_structure"


def test_non_target_family_returns_none():
    assert (
        _refine_polynomial_unknown_mechanism(
            "F5",
            recognized_expression="x+1",
            final_expression="x+1",
            expected_answer="x+2",
            question_text="(x+1)+1",
        )
        is None
    )


def test_structured_analysis_merges_refine_when_infer_unknown_f1():
    r = _handwriting_structured_analysis(
        "12x+10",
        "10",
        "6x + 1 - 6x + 9",
        "F1",
    )
    assert r["error_mechanism"] == "combine_error"
    assert r["step_focus"] == "like_terms"
    assert r["issue_tag"] == "combine_error"
