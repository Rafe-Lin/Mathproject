# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfIntegers
family_id: I3
family_name: int_flat_mul_div_exact
subskill_nodes: ["sign_handling", "mul_div", "exact_divisibility"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【I3】int_flat_mul_div_exact（level={}）".format(level)
    answer = "I3_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "I3",
        "subskill_nodes": ["sign_handling", "mul_div", "exact_divisibility"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
