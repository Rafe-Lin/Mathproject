# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F5
family_name: Fraction Add/Subtract
subskill_nodes: ["add_sub", "nested_parentheses", "mixed_numbers"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F5】Fraction Add/Subtract（level={}）".format(level)
    answer = "F5_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F5",
        "subskill_nodes": ["add_sub", "nested_parentheses", "mixed_numbers"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
