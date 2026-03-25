# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F4
family_name: poly_mul_monomial
subskill_nodes: ["expand_monomial"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F4】poly_mul_monomial（level={}）".format(level)
    answer = "F4_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F4",
        "subskill_nodes": ["expand_monomial"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
