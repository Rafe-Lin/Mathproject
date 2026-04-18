# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F12
family_name: poly_geom_formula_direct
subskill_nodes: ["geometry_formula"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F12】poly_geom_formula_direct（level={}）".format(level)
    answer = "F12_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F12",
        "subskill_nodes": ["geometry_formula"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
