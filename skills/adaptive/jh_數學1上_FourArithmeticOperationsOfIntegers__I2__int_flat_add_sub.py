# -*- coding: utf-8 -*-
from __future__ import annotations

import random


def generate(level=1):
    count = random.choice([3, 4, 4, 5])
    nums = [random.randint(-18, 18) for _ in range(count)]
    if all(n == 0 for n in nums):
        nums[0] = random.randint(1, 9)
    answer = sum(nums)
    expr = " ".join([str(nums[0])] + [f"{n:+d}" for n in nums[1:]])
    question_text = f"請計算：{expr}"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": expr,
        "answer": str(answer),
        "correct_answer": str(answer),
        "explanation": "依序處理每一項，負號要跟著數字一起算。",
        "family_id": "I2",
        "family_name": "int_flat_add_sub",
        "subskill_nodes": ["sign_handling", "add_sub"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
