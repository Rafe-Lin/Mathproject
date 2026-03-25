# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F5
family_name: poly_mul_poly
subskill_nodes: ["expand_binomial", "combine_like_terms"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F5】poly_mul_poly（level={}）".format(level)
    answer = "F5_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F5",
        "subskill_nodes": ["expand_binomial", "combine_like_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
