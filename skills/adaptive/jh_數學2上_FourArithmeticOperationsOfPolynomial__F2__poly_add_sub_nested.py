# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F2
family_name: poly_add_sub_nested
subskill_nodes: ["sign_distribution", "combine_like_terms", "family_isomorphism"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F2】poly_add_sub_nested（level={}）".format(level)
    answer = "F2_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F2",
        "subskill_nodes": ["sign_distribution", "combine_like_terms", "family_isomorphism"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
