# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def _non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def _fmt_signed(value: int) -> str:
    return f"+ {value}" if value >= 0 else f"- {abs(value)}"


def _fmt_x_term(coeff: int, with_sign: bool = False) -> str:
    abs_coeff = abs(coeff)
    core = "x" if abs_coeff == 1 else f"{abs_coeff}x"
    if with_sign:
        return f"+ {core}" if coeff >= 0 else f"- {core}"
    return core if coeff >= 0 else f"-{core}"


def _fmt_linear(coeff: int, const: int) -> str:
    parts: list[str] = []
    if coeff != 0:
        parts.append(_fmt_x_term(coeff, with_sign=False))
    if const != 0:
        if parts:
            parts.append(_fmt_signed(const))
        else:
            parts.append(str(const))
    if not parts:
        return "0"
    return " ".join(parts)


def generate(level=1):
    term_count = random.choice([3, 4, 4, 5])
    x_coeffs = [random.choice([0, _non_zero(-9, 9)]) for _ in range(term_count)]
    const_terms = [random.randint(-12, 12) for _ in range(term_count)]
    if all(c == 0 for c in x_coeffs):
        x_coeffs[random.randrange(term_count)] = _non_zero(-8, 8)

    coeff_sum = sum(x_coeffs)
    const_sum = sum(const_terms)
    while coeff_sum == 0 and const_sum == 0:
        const_terms[random.randrange(term_count)] = random.randint(-12, 12)
        coeff_sum = sum(x_coeffs)
        const_sum = sum(const_terms)

    rendered_terms: list[str] = []
    for coeff, const in zip(x_coeffs, const_terms):
        if coeff != 0:
            rendered_terms.append(_fmt_x_term(coeff, with_sign=bool(rendered_terms)))
        if const != 0:
            rendered_terms.append(_fmt_signed(const) if rendered_terms else str(const))
    expr = " ".join(rendered_terms)
    answer = _fmt_linear(coeff_sum, const_sum)

    question_text = f"化簡：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": answer,
        "correct_answer": answer,
        "explanation": "先把 x 項合併，再把常數項相加。",
        "family_id": "F1",
        "family_name": "poly_add_sub_flat",
        "subskill_nodes": ["normalize_terms", "combine_like_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).replace(" ", "") == str(correct_answer).replace(" ", "")
