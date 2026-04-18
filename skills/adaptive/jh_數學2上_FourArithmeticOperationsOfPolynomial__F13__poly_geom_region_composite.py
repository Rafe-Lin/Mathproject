# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourArithmeticOperationsOfPolynomial
family_id: F13
family_name: poly_geom_region_composite
subskill_nodes: ["geometry_formula", "composite_region_modeling"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F13】poly_geom_region_composite（level={}）".format(level)
    answer = "F13_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F13",
        "subskill_nodes": ["geometry_formula", "composite_region_modeling"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
