# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfIntegers
family_id: I6
family_name: int_abs_value
subskill_nodes: ["sign_handling", "absolute_value"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【I6】int_abs_value（level={}）".format(level)
    answer = "I6_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "I6",
        "subskill_nodes": ["sign_handling", "absolute_value"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
