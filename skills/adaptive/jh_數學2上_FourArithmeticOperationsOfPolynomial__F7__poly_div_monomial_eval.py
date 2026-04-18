# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F7
family_name: poly_div_monomial_eval
subskill_nodes: ["normalize_terms"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F7】poly_div_monomial_eval（level={}）".format(level)
    answer = "F7_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F7",
        "subskill_nodes": ["normalize_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
