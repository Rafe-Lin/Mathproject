# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F3
family_name: poly_add_sub_unknown
subskill_nodes: ["sign_distribution", "unknown_target_preservation"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F3】poly_add_sub_unknown（level={}）".format(level)
    answer = "F3_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F3",
        "subskill_nodes": ["sign_distribution", "unknown_target_preservation"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
