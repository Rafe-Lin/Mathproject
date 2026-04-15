# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from typing import Any

from .textbook_progression import get_prerequisite_candidates


LINEAR_SUBSKILLS = {
    "coefficient_sign_handling",
    "like_term_combination",
    "term_collection_with_constants",
    "outer_minus_scope",
    "monomial_distribution",
    "nested_bracket_scope",
    "structure_isomorphism",
    "fractional_expression_simplification",
}

INTEGER_POWER_SUBSKILLS = {
    "power_notation_basics",
    "signed_power_interpretation",
    "parenthesized_negative_base",
    "minus_outside_power",
    "power_precedence_in_mixed_ops",
    "signed_power_evaluation",
    "mixed_power_arithmetic",
}

NUMBER_POWER_SUBSKILLS = {
    "same_base_multiplication_rule",
    "power_building_from_repetition",
    "power_of_power_rule",
    "product_power_distribution",
    "fraction_power_distribution",
}


def _has_power_signal(*, question_text: str, correct_answer: str, student_answer: str) -> bool:
    text = " ".join(
        [
            str(question_text or ""),
            str(correct_answer or ""),
            str(student_answer or ""),
        ]
    ).lower()
    if not text.strip():
        return False
    # Use strong keywords only; avoid treating generic polynomial x^2 as power-remediation trigger.
    power_keywords = (
        "次方",
        "指數",
        "乘方",
        "冪",
        "exponent",
        "power rule",
        "power of power",
        "same base",
        "i9",
        "i10",
    )
    if any(k in text for k in power_keywords):
        return True
    if re.search(r"\(-?[a-z0-9]+\)\s*\^\s*\d+", text):
        return True
    return False


def _rank_candidate_priority(code: str) -> int:
    key = str(code or "").strip()
    # Prefer remediation for distribution / bracket / sign / like-term / basic arithmetic first.
    priority = {
        "outer_minus_scope": 0,
        "monomial_distribution": 1,
        "like_term_combination": 2,
        "combine_after_distribution": 3,
        "nested_bracket_scope": 4,
        "coefficient_sign_handling": 5,
        "term_collection_with_constants": 6,
        "sign_handling": 7,
        "add_sub": 8,
        "mul_div": 9,
        "order_of_operations": 10,
        "expand_structure": 11,
    }
    if key in priority:
        return priority[key]
    if key in LINEAR_SUBSKILLS:
        return 20
    if key in INTEGER_POWER_SUBSKILLS:
        return 80
    if key in NUMBER_POWER_SUBSKILLS:
        return 90
    return 50


def _infer_candidate_skill(code: str) -> str:
    key = str(code or "").strip()
    if key in LINEAR_SUBSKILLS:
        return "linear_expression_arithmetic"
    if key in NUMBER_POWER_SUBSKILLS:
        return "fraction_arithmetic"
    if key in INTEGER_POWER_SUBSKILLS:
        return "integer_arithmetic"
    return "integer_arithmetic"


def retrieve_remediation_candidates(
    *,
    skill_id: str,
    family_id: str,
    question_text: str = "",
    correct_answer: str = "",
    student_answer: str = "",
    top_k: int = 3,
) -> dict[str, Any]:
    """Minimal retriever interface; current source is textbook progression YAML."""
    candidates = get_prerequisite_candidates(skill_id, family_id)
    if not isinstance(candidates, list):
        candidates = []
    out: list[dict[str, Any]] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        normalized = {str(k): v for k, v in item.items()}
        code = str(normalized.get("code") or normalized.get("runtime_subskill") or "").strip()
        normalized["prereq_skill"] = str(normalized.get("prereq_skill") or _infer_candidate_skill(code))
        normalized["candidate_source"] = str(normalized.get("candidate_source") or "textbook_prerequisite")
        out.append(normalized)
    # For polynomial families (especially F2/F5/F11), avoid accidental jump to power remediation
    # unless there is explicit power/exponent diagnostic signal.
    family = str(family_id or "").strip().upper()
    if family in {"F2", "F5", "F11"}:
        power_signal = _has_power_signal(
            question_text=question_text,
            correct_answer=correct_answer,
            student_answer=student_answer,
        )
        if not power_signal:
            out = sorted(
                out,
                key=lambda item: _rank_candidate_priority(
                    str(item.get("code") or item.get("runtime_subskill") or "")
                ),
            )
    out = out[: max(1, int(top_k))]
    candidate_codes = [str(item.get("code") or item.get("runtime_subskill") or "").strip() for item in out]
    candidate_descriptions = {
        str(item.get("code") or item.get("runtime_subskill") or "").strip(): str(item.get("description") or "")
        for item in out
        if str(item.get("code") or item.get("runtime_subskill") or "").strip()
    }
    return {
        "candidate_codes": candidate_codes,
        "candidate_descriptions": candidate_descriptions,
        "candidates": out,
        "candidate_source": "textbook_prerequisite",
        "retrieval_source": "textbook_progression_yaml",
        "retrieval_confidence": None,
        "query_snapshot": {
            "question_text": str(question_text or ""),
            "correct_answer": str(correct_answer or ""),
            "student_answer": str(student_answer or ""),
        },
    }
