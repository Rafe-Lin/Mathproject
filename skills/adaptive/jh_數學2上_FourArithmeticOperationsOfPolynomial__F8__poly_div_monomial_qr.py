# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F8
family_name: poly_div_monomial_qr
subskill_nodes: ["long_division", "quotient_remainder_format"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F8】poly_div_monomial_qr（level={}）".format(level)
    answer = "F8_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F8",
        "subskill_nodes": ["long_division", "quotient_remainder_format"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
