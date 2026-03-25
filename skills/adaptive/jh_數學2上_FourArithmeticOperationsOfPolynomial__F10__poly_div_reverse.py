# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F10
family_name: poly_div_reverse
subskill_nodes: ["reverse_division_reconstruction"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F10】poly_div_reverse（level={}）".format(level)
    answer = "F10_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F10",
        "subskill_nodes": ["reverse_division_reconstruction"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
