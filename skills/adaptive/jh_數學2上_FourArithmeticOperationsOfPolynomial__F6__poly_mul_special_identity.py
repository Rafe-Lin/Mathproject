# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F6
family_name: poly_mul_special_identity
subskill_nodes: ["special_identity"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F6】poly_mul_special_identity（level={}）".format(level)
    answer = "F6_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F6",
        "subskill_nodes": ["special_identity"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
