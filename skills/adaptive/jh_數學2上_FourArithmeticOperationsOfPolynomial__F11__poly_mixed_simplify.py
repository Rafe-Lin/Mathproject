# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F11
family_name: poly_mixed_simplify
subskill_nodes: ["expand_binomial", "special_identity", "combine_like_terms", "family_isomorphism"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F11】poly_mixed_simplify（level={}）".format(level)
    answer = "F11_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F11",
        "subskill_nodes": ["expand_binomial", "special_identity", "combine_like_terms", "family_isomorphism"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
