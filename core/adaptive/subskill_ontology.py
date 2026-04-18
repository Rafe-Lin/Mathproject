from __future__ import annotations

from typing import Final

from .agent_skill_schema import AGENT_SKILL_SUBSKILLS


# Canonical runtime subskill aliases (diagnosis namespace -> runtime namespace).
RUNTIME_SUBSKILL_ALIASES: Final[dict[str, dict[str, str]]] = {
    "integer_arithmetic": {
        "signed_arithmetic": "sign_handling",
        "division": "mul_div",
        "basic_operations": "add_sub",
        "bracket_scope": "parentheses",
        "outer_minus_scope": "parentheses",
        "order_of_operations": "mixed_ops",
        "structure_isomorphism": "mixed_ops",
        "expand_structure": "mul_div",
        "coefficient_arithmetic": "mul_div",
        "sign_distribution": "sign_handling",
        "sign_flip_after_distribution": "sign_handling",
        "combine_after_distribution": "add_sub",
        "power_sign_parentheses_confusion": "signed_power_interpretation",
        "power_precedence_confusion": "power_precedence_in_mixed_ops",
    },
    "fraction_arithmetic": {
        "same_base_power_rule_error": "same_base_multiplication_rule",
        "power_of_power_rule_error": "power_of_power_rule",
        "product_power_distribution_error": "product_power_distribution",
    },
    "linear_expression_arithmetic": {
        "outer_minus_scope": "outer_minus_scope",
        "sign_distribution": "monomial_distribution",
        "sign_flip_after_distribution": "outer_minus_scope",
        "combine_like_terms_after_distribution": "like_term_combination",
        "coefficient_arithmetic": "coefficient_sign_handling",
        "coefficient_arithmetic_error": "coefficient_sign_handling",
        "nested_grouping_structure_error": "nested_bracket_scope",
        "mixed_simplify_transition_error": "nested_bracket_scope",
        "family_isomorphism_confusion": "structure_isomorphism",
        "basic_operations": "term_collection_with_constants",
    },
}


# Error-concept fallback when diagnosis subskill is empty/unknown.
ERROR_CONCEPT_CANONICAL_RUNTIME_SUBSKILL: Final[dict[tuple[str, str, str], str]] = {
    ("polynomial_arithmetic", "integer_arithmetic", "negative_sign_handling"): "sign_handling",
    ("polynomial_arithmetic", "integer_arithmetic", "division_misconception"): "mul_div",
    ("polynomial_arithmetic", "integer_arithmetic", "basic_arithmetic_instability"): "add_sub",
    ("polynomial_arithmetic", "integer_arithmetic", "outer_minus_scope"): "parentheses",
    ("polynomial_arithmetic", "integer_arithmetic", "bracket_scope_error"): "parentheses",
    ("polynomial_arithmetic", "integer_arithmetic", "sign_distribution"): "sign_handling",
    ("polynomial_arithmetic", "integer_arithmetic", "sign_flip_after_distribution"): "sign_handling",
    ("polynomial_arithmetic", "integer_arithmetic", "combine_like_terms_after_distribution"): "add_sub",
    ("polynomial_arithmetic", "integer_arithmetic", "coefficient_arithmetic_error"): "mul_div",
    ("polynomial_arithmetic", "integer_arithmetic", "nested_grouping_structure_error"): "parentheses",
    ("polynomial_arithmetic", "integer_arithmetic", "binomial_expansion_structure_error"): "mul_div",
    ("polynomial_arithmetic", "integer_arithmetic", "mixed_simplify_transition_error"): "mixed_ops",
    ("polynomial_arithmetic", "integer_arithmetic", "family_isomorphism_confusion"): "mixed_ops",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "outer_minus_scope"): "outer_minus_scope",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "sign_distribution"): "monomial_distribution",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "sign_flip_after_distribution"): "outer_minus_scope",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "combine_like_terms_after_distribution"): "like_term_combination",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "coefficient_arithmetic_error"): "coefficient_sign_handling",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "nested_grouping_structure_error"): "nested_bracket_scope",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "mixed_simplify_transition_error"): "nested_bracket_scope",
    ("polynomial_arithmetic", "linear_expression_arithmetic", "family_isomorphism_confusion"): "structure_isomorphism",
    ("polynomial_arithmetic", "integer_arithmetic", "power_sign_parentheses_confusion"): "signed_power_interpretation",
    ("polynomial_arithmetic", "integer_arithmetic", "power_precedence_confusion"): "power_precedence_in_mixed_ops",
    ("polynomial_arithmetic", "fraction_arithmetic", "same_base_power_rule_error"): "same_base_multiplication_rule",
    ("polynomial_arithmetic", "fraction_arithmetic", "power_of_power_rule_error"): "power_of_power_rule",
    ("polynomial_arithmetic", "fraction_arithmetic", "product_power_distribution_error"): "product_power_distribution",
}


def normalize_runtime_subskill(
    raw_subskill: str | None,
    *,
    target_agent_skill: str | None,
    origin_agent_skill: str | None = None,
    error_concept: str | None = None,
) -> str:
    target = str(target_agent_skill or "").strip()
    origin = str(origin_agent_skill or "").strip()
    concept = str(error_concept or "").strip()
    raw = str(raw_subskill or "").strip()
    if not target:
        return raw

    aliases = RUNTIME_SUBSKILL_ALIASES.get(target, {})
    if raw in aliases:
        return aliases[raw]
    if raw:
        return raw

    fallback = ERROR_CONCEPT_CANONICAL_RUNTIME_SUBSKILL.get((origin, target, concept))
    if fallback:
        return fallback
    return raw


def is_runtime_subskill_valid(agent_skill: str | None, subskill: str | None) -> bool:
    agent = str(agent_skill or "").strip()
    sub = str(subskill or "").strip()
    if not agent or not sub:
        return False
    return sub in set(AGENT_SKILL_SUBSKILLS.get(agent, []))
