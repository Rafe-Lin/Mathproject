# -*- coding: utf-8 -*-

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.evaluate_mcri import (
    analyze_code_robustness,
    evaluate_live_code,
    evaluate_math_hygiene,
)


def test_evaluate_math_hygiene_rewards_clean_latex():
    score, notes = evaluate_math_hygiene(r"$\frac{2}{3}\times\frac{\sqrt{3}}{3}$")
    assert score >= 14
    assert notes == []


def test_analyze_code_robustness_flags_empty_code():
    grade, reason = analyze_code_robustness("")
    assert grade == "SYNTAX_ERROR"
    assert "empty" in reason


def test_evaluate_live_code_returns_full_payload():
    result = evaluate_live_code(
        code=(
            "def generate(level=1):\n"
            "    return {'question_text': r'$3+5$', 'correct_answer': '8'}\n"
        ),
        exec_result={"question_text": r"$3+5$", "correct_answer": "8"},
        healer_trace={"regex_fixes": 0, "ast_fixes": 0},
        ablation_mode=False,
    )

    assert result["total_score"] > 0
    assert set(result) >= {
        "syntax_score",
        "logic_score",
        "render_score",
        "stability_score",
        "total_score",
        "breakdown",
    }
    assert "l4_3_hygiene" in result["breakdown"]
