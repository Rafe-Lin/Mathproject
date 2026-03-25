# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfIntegers
family_id: I5
family_name: int_bracket_mixed
subskill_nodes: ["sign_handling", "bracket_scope", "order_of_operations"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【I5】int_bracket_mixed（level={}）".format(level)
    answer = "I5_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "I5",
        "subskill_nodes": ["sign_handling", "bracket_scope", "order_of_operations"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
