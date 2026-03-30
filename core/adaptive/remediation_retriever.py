# -*- coding: utf-8 -*-
from __future__ import annotations

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
