from __future__ import annotations

from typing import Final

AGENT_SKILL_INTEGER_ARITHMETIC: Final[str] = "integer_arithmetic"
AGENT_SKILL_FRACTION_ARITHMETIC: Final[str] = "fraction_arithmetic"
AGENT_SKILL_RADICAL_ARITHMETIC: Final[str] = "radical_arithmetic"
AGENT_SKILL_POLYNOMIAL_ARITHMETIC: Final[str] = "polynomial_arithmetic"
AGENT_SKILL_LINEAR_EXPRESSION_ARITHMETIC: Final[str] = "linear_expression_arithmetic"

AGENT_SKILLS: Final[tuple[str, ...]] = (
    AGENT_SKILL_INTEGER_ARITHMETIC,
    AGENT_SKILL_FRACTION_ARITHMETIC,
    AGENT_SKILL_RADICAL_ARITHMETIC,
    AGENT_SKILL_POLYNOMIAL_ARITHMETIC,
    AGENT_SKILL_LINEAR_EXPRESSION_ARITHMETIC,
)

AGENT_SKILL_SUBSKILLS: Final[dict[str, list[str]]] = {
    AGENT_SKILL_INTEGER_ARITHMETIC: [
        "sign_handling",
        "add_sub",
        "mul_div",
        "mixed_ops",
        "absolute_value",
        "parentheses",
        "power_notation_basics",
        "signed_power_interpretation",
        "parenthesized_negative_base",
        "minus_outside_power",
        "power_precedence_in_mixed_ops",
        "signed_power_evaluation",
        "mixed_power_arithmetic",
    ],
    AGENT_SKILL_FRACTION_ARITHMETIC: [
        "proper_improper_fraction",
        "mixed_numbers",
        "sign_normalization",
        "simplest_form_reduction",
        "equivalent_fraction_scaling",
        "fraction_add_sub",
        "fraction_mul_div",
        "reciprocal",
        "same_base_multiplication_rule",
        "power_building_from_repetition",
        "power_of_power_rule",
        "product_power_distribution",
        "fraction_power_distribution",
    ],
    AGENT_SKILL_RADICAL_ARITHMETIC: [
        "radical_simplify",
        "radical_mul_div",
        "radical_add_sub",
        "conjugate_rationalize",
    ],
    AGENT_SKILL_POLYNOMIAL_ARITHMETIC: [
        "poly_add_sub",
        "poly_mul_monomial",
        "poly_mul_poly",
        "poly_expand",
        "poly_formula",
    ],
    AGENT_SKILL_LINEAR_EXPRESSION_ARITHMETIC: [
        "coefficient_sign_handling",
        "like_term_combination",
        "term_collection_with_constants",
        "outer_minus_scope",
        "monomial_distribution",
        "nested_bracket_scope",
        "structure_isomorphism",
        "fractional_expression_simplification",
    ],
}

SYSTEM_SKILL_TO_AGENT_SKILL: Final[dict[str, str]] = {
    "jh_??1?_FourArithmeticOperationsOfIntegers": AGENT_SKILL_INTEGER_ARITHMETIC,
    "jh_??1?_FourArithmeticOperationsOfNumbers": AGENT_SKILL_FRACTION_ARITHMETIC,
    "jh_??2?_FourOperationsOfRadicals": AGENT_SKILL_RADICAL_ARITHMETIC,
    "jh_??2?_FourArithmeticOperationsOfPolynomial": AGENT_SKILL_POLYNOMIAL_ARITHMETIC,
}


def resolve_agent_skill(system_skill_id: str) -> str | None:
    key = str(system_skill_id or "").strip()
    hit = SYSTEM_SKILL_TO_AGENT_SKILL.get(key)
    if hit:
        return hit
    if key.endswith("FourArithmeticOperationsOfIntegers"):
        return AGENT_SKILL_INTEGER_ARITHMETIC
    if key.endswith("FourArithmeticOperationsOfNumbers"):
        return AGENT_SKILL_FRACTION_ARITHMETIC
    if key.endswith("FourOperationsOfRadicals"):
        return AGENT_SKILL_RADICAL_ARITHMETIC
    if key.endswith("FourArithmeticOperationsOfPolynomial"):
        return AGENT_SKILL_POLYNOMIAL_ARITHMETIC
    if key.endswith("OperationsOnLinearExpressions"):
        return AGENT_SKILL_LINEAR_EXPRESSION_ARITHMETIC
    return None
