from __future__ import annotations

from typing import Final

AGENT_SKILL_INTEGER_ARITHMETIC: Final[str] = "integer_arithmetic"
AGENT_SKILL_FRACTION_ARITHMETIC: Final[str] = "fraction_arithmetic"
AGENT_SKILL_RADICAL_ARITHMETIC: Final[str] = "radical_arithmetic"
AGENT_SKILL_POLYNOMIAL_ARITHMETIC: Final[str] = "polynomial_arithmetic"

AGENT_SKILLS: Final[tuple[str, ...]] = (
    AGENT_SKILL_INTEGER_ARITHMETIC,
    AGENT_SKILL_FRACTION_ARITHMETIC,
    AGENT_SKILL_RADICAL_ARITHMETIC,
    AGENT_SKILL_POLYNOMIAL_ARITHMETIC,
)

AGENT_SKILL_SUBSKILLS: Final[dict[str, list[str]]] = {
    AGENT_SKILL_INTEGER_ARITHMETIC: [
        "sign_handling",
        "add_sub",
        "mul_div",
        "mixed_ops",
        "absolute_value",
        "parentheses",
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
}

SYSTEM_SKILL_TO_AGENT_SKILL: Final[dict[str, str]] = {
    "jh_數學1上_FourArithmeticOperationsOfIntegers": AGENT_SKILL_INTEGER_ARITHMETIC,
    "jh_數學1上_FourArithmeticOperationsOfNumbers": AGENT_SKILL_FRACTION_ARITHMETIC,
    "jh_數學2上_FourOperationsOfRadicals": AGENT_SKILL_RADICAL_ARITHMETIC,
    "jh_數學2上_FourArithmeticOperationsOfPolynomial": AGENT_SKILL_POLYNOMIAL_ARITHMETIC,
}


def resolve_agent_skill(system_skill_id: str) -> str | None:
    return SYSTEM_SKILL_TO_AGENT_SKILL.get(str(system_skill_id or "").strip())
