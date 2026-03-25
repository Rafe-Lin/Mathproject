# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F9
family_name: Decimal-Fraction Mixed Evaluation
subskill_nodes: ["decimal_to_fraction_exact_conversion", "add_sub", "multiply", "divide", "nested_parentheses"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F9】Decimal-Fraction Mixed Evaluation（level={}）".format(level)
    answer = "F9_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F9",
        "subskill_nodes": ["decimal_to_fraction_exact_conversion", "add_sub", "multiply", "divide", "nested_parentheses"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
