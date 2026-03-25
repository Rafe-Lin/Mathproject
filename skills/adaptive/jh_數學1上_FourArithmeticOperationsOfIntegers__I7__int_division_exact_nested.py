# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfIntegers
family_id: I7
family_name: int_division_exact_nested
subskill_nodes: ["sign_handling", "mul_div", "bracket_scope", "absolute_value", "exact_divisibility"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【I7】int_division_exact_nested（level={}）".format(level)
    answer = "I7_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "I7",
        "subskill_nodes": ["sign_handling", "mul_div", "bracket_scope", "absolute_value", "exact_divisibility"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
