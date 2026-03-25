# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfIntegers
family_id: I4
family_name: int_flat_mixed_four_ops
subskill_nodes: ["sign_handling", "add_sub", "mul_div", "order_of_operations"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【I4】int_flat_mixed_four_ops（level={}）".format(level)
    answer = "I4_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "I4",
        "subskill_nodes": ["sign_handling", "add_sub", "mul_div", "order_of_operations"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
