# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfIntegers
family_id: I8
family_name: int_composite_structure
subskill_nodes: ["sign_handling", "add_sub", "mul_div", "order_of_operations", "bracket_scope", "absolute_value", "exact_divisibility", "isomorphic_structure"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【I8】int_composite_structure（level={}）".format(level)
    answer = "I8_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "I8",
        "subskill_nodes": ["sign_handling", "add_sub", "mul_div", "order_of_operations", "bracket_scope", "absolute_value", "exact_divisibility", "isomorphic_structure"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
