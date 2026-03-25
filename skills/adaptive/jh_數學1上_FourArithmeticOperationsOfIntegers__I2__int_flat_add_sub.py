# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfIntegers
family_id: I2
family_name: int_flat_add_sub
subskill_nodes: ["sign_handling", "add_sub"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【I2】int_flat_add_sub（level={}）".format(level)
    answer = "I2_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "I2",
        "subskill_nodes": ["sign_handling", "add_sub"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
