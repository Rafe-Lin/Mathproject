from __future__ import annotations

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.adaptive.rag_hint_engine import build_rag_hint


def test_integer_rag_hint_is_chinese_and_domain_specific():
    result = build_rag_hint(
        subskill_nodes=["sign_handling", "add_sub"],
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        family_id="I2",
        question_context="計算下列各式的值：5 + 14 - 7",
        question_text="計算下列各式的值：5 + 14 - 7",
    )

    assert result["source"] == "hybrid_rag"
    assert result["subskill_labels"] == ["正負號判讀", "整數加減"]
    assert "整數四則重點" in result["hint_html"]
    assert "正負號判讀" in result["hint_html"]
    assert "add_sub" not in result["hint_html"]


def test_radical_rag_hint_includes_rationalization_tip():
    result = build_rag_hint(
        subskill_nodes=["divide_terms", "conjugate_rationalize"],
        skill_id="jh_數學2上_FourOperationsOfRadicals",
        family_id="p5b",
        question_context="化簡 1/(sqrt(3)-1)",
        question_text="化簡 1/(sqrt(3)-1)",
    )

    assert result["source"] == "hybrid_rag"
    assert "分母有理化" in result["hint_html"]
    assert "共軛" in result["hint_html"]
    assert "divide_terms" not in result["hint_html"]
