# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def _non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def generate(level=1):
    a = random.randint(-15, 15)
    b = random.randint(-10, 10)
    c = _non_zero(-6, 6)
    d = random.randint(-12, 12)
    answer = a + b * c - d
    expr = f"{a} {b:+d}×{c} {-d:+d}"
    question_text = f"請計算：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": str(answer),
        "correct_answer": str(answer),
        "explanation": "先做乘法，再做加減。",
        "family_id": "I4",
        "family_name": "int_flat_mixed_four_ops",
        "subskill_nodes": ["sign_handling", "mul_div", "add_sub"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
