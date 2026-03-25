# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p2h
family_name: p2h_frac_mult_rad
subskill_nodes: ["multiply_terms", "fractional_radical"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p2h】p2h_frac_mult_rad（level={}）".format(level)
    answer = "p2h_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p2h",
        "subskill_nodes": ["multiply_terms", "fractional_radical"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
