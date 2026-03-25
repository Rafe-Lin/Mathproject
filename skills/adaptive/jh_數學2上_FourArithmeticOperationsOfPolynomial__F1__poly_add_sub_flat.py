# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F1
family_name: poly_add_sub_flat
subskill_nodes: ["normalize_terms", "combine_like_terms"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F1】poly_add_sub_flat（level={}）".format(level)
    answer = "F1_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F1",
        "subskill_nodes": ["normalize_terms", "combine_like_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
