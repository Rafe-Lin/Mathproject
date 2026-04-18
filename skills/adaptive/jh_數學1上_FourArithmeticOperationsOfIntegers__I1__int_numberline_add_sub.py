# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def _non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def generate(level=1):
    a = random.randint(-20, 20)
    b = _non_zero(-15, 15)
    answer = a + b
    expr = f"{a} {b:+d}"
    question_text = f"請計算：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": str(answer),
        "correct_answer": str(answer),
        "explanation": "先判斷正負方向，再做整數加減。",
        "family_id": "I1",
        "family_name": "int_numberline_add_sub",
        "subskill_nodes": ["sign_handling", "add_sub"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
