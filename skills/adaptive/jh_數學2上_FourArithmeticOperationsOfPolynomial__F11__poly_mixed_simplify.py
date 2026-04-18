# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def _non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def _fmt_term(coeff: int, power: int, with_sign: bool = False) -> str:
    if coeff == 0:
        return ""
    abs_coeff = abs(coeff)
    if power == 2:
        core = "x^2" if abs_coeff == 1 else f"{abs_coeff}x^2"
    elif power == 1:
        core = "x" if abs_coeff == 1 else f"{abs_coeff}x"
    else:
        core = str(abs_coeff)
    if with_sign:
        return f"+ {core}" if coeff >= 0 else f"- {core}"
    return core if coeff >= 0 else f"-{core}"


def _fmt_poly(coeff2: int, coeff1: int, coeff0: int) -> str:
    parts: list[str] = []
    for coeff, power in ((coeff2, 2), (coeff1, 1), (coeff0, 0)):
        if coeff != 0:
            parts.append(_fmt_term(coeff, power, with_sign=bool(parts)))
    return " ".join(parts) if parts else "0"


def generate(level=1):
    pattern = random.choice(["triple_linear", "binomial_square_plus_linear"])
    if pattern == "triple_linear":
        a, b = _non_zero(-6, 6), random.randint(-9, 9)
        c, d = _non_zero(-6, 6), random.randint(-9, 9)
        e, f = _non_zero(-6, 6), random.randint(-9, 9)
        coeff2, coeff1, coeff0 = 0, a + c - e, b + d - f
        expr = f"({a}x {b:+d}) + ({c}x {d:+d}) - ({e}x {f:+d})"
    else:
        m, n = random.randint(-6, 6), random.randint(-6, 6)
        p, q = _non_zero(-8, 8), random.randint(-12, 12)
        coeff2, coeff1, coeff0 = 1, m + n + p, m * n + q
        expr = f"(x {m:+d})(x {n:+d}) {p:+d}x {q:+d}"

    if coeff2 == 0 and coeff1 == 0 and coeff0 == 0:
        coeff0 = 1
    answer = _fmt_poly(coeff2, coeff1, coeff0)
    question_text = f"化簡：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": answer,
        "correct_answer": answer,
        "explanation": "先展開括號，再合併同類項，最後依次方由高到低排列。",
        "family_id": "F11",
        "family_name": "poly_mixed_simplify",
        "subskill_nodes": ["expand_binomial", "combine_like_terms", "family_isomorphism"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).replace(" ", "") == str(correct_answer).replace(" ", "")
