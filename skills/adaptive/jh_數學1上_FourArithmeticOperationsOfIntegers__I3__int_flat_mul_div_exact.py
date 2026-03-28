# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def _non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def generate(level=1):
    a = _non_zero(-9, 9)
    b = _non_zero(-9, 9)
    if random.choice([True, False]):
        expr = f"{a} × {b}"
        answer = a * b
    else:
        expr = f"{a * b} ÷ {b}"
        answer = a
    question_text = f"請計算：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": str(answer),
        "correct_answer": str(answer),
        "explanation": "先判斷正負，再算乘除；除法題都可整除。",
        "family_id": "I3",
        "family_name": "int_flat_mul_div_exact",
        "subskill_nodes": ["sign_handling", "mul_div"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
