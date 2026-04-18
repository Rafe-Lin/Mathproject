# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F8
family_name: Reciprocal
subskill_nodes: ["reciprocal_transform"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F8】Reciprocal（level={}）".format(level)
    answer = "F8_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F8",
        "subskill_nodes": ["reciprocal_transform"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
