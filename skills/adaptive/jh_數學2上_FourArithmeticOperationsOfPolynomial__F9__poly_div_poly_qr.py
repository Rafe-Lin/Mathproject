# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F9
family_name: poly_div_poly_qr
subskill_nodes: ["long_division", "quotient_remainder_format"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F9】poly_div_poly_qr（level={}）".format(level)
    answer = "F9_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F9",
        "subskill_nodes": ["long_division", "quotient_remainder_format"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
