# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def _non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def _fmt_poly(coeff2: int, coeff1: int, coeff0: int) -> str:
    parts: list[str] = []
    if coeff2 != 0:
        if coeff2 == 1:
            parts.append("x^2")
        elif coeff2 == -1:
            parts.append("-x^2")
        else:
            parts.append(f"{coeff2}x^2")
    if coeff1 != 0:
        if parts:
            if coeff1 == 1:
                parts.append("+ x")
            elif coeff1 == -1:
                parts.append("- x")
            elif coeff1 > 0:
                parts.append(f"+ {coeff1}x")
            else:
                parts.append(f"- {abs(coeff1)}x")
        else:
            if coeff1 == 1:
                parts.append("x")
            elif coeff1 == -1:
                parts.append("-x")
            else:
                parts.append(f"{coeff1}x")
    if coeff0 != 0:
        if parts:
            parts.append(f"+ {coeff0}" if coeff0 > 0 else f"- {abs(coeff0)}")
        else:
            parts.append(str(coeff0))
    return " ".join(parts) if parts else "0"


def generate(level=1):
    a, c = _non_zero(-6, 6), _non_zero(-6, 6)
    b, d = random.randint(-9, 9), random.randint(-9, 9)
    coeff2 = a * c
    coeff1 = a * d + b * c
    coeff0 = b * d
    if coeff2 == 0 and coeff1 == 0 and coeff0 == 0:
        coeff0 = 1
    expr = f"({a}x {b:+d})({c}x {d:+d})"
    answer = _fmt_poly(coeff2, coeff1, coeff0)
    question_text = f"展開並化簡：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": answer,
        "correct_answer": answer,
        "explanation": "用分配律展開兩個括號，再合併同類項。",
        "family_id": "F5",
        "family_name": "poly_mul_poly",
        "subskill_nodes": ["expand_binomial", "combine_like_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).replace(" ", "") == str(correct_answer).replace(" ", "")
