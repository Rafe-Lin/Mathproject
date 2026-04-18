# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def _non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def generate(level=1):
    q = _non_zero(-8, 8)
    divisor = random.choice([-4, -3, -2, 2, 3, 4])
    dividend = q * divisor
    bonus = random.randint(-9, 9)
    answer = q + bonus
    expr = f"({dividend} ÷ {divisor}) {bonus:+d}"
    question_text = f"請計算：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": str(answer),
        "correct_answer": str(answer),
        "explanation": "先完成括號中的整除，再與後面的整數相加減。",
        "family_id": "I7",
        "family_name": "int_division_exact_nested",
        "subskill_nodes": ["sign_handling", "mul_div", "add_sub"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
