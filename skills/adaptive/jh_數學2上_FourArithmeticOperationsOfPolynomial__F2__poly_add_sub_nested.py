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


def _fmt_x(coeff: int) -> str:
    if coeff == 1:
        return "x"
    if coeff == -1:
        return "-x"
    return f"{coeff}x"


def _fmt_linear(coeff: int, const: int) -> str:
    parts: list[str] = []
    if coeff != 0:
        parts.append(_fmt_x(coeff))
    if const != 0:
        if parts:
            parts.append(_fmt_signed(const))
        else:
            parts.append(str(const))
    return " ".join(parts) if parts else "0"


def generate(level=1):
    a, b = _non_zero(-8, 8), random.randint(-12, 12)
    c, d = _non_zero(-8, 8), random.randint(-12, 12)
    e, f = _non_zero(-8, 8), random.randint(-12, 12)

    pattern = random.choice(["plus_minus", "minus_plus"])
    if pattern == "plus_minus":
        coeff = a + c - e
        const = b + d - f
        expr = f"({a}x {b:+d}) + ({c}x {d:+d}) - ({e}x {f:+d})"
    else:
        coeff = a - c + e
        const = b - d + f
        expr = f"({a}x {b:+d}) - ({c}x {d:+d}) + ({e}x {f:+d})"

    if coeff == 0 and const == 0:
        const = 1
    answer = _fmt_linear(coeff, const)

    question_text = f"化簡：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": answer,
        "correct_answer": answer,
        "explanation": "先處理括號前的正負號，再合併同類項。",
        "family_id": "F2",
        "family_name": "poly_add_sub_nested",
        "subskill_nodes": ["sign_distribution", "combine_like_terms", "family_isomorphism"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).replace(" ", "") == str(correct_answer).replace(" ", "")
