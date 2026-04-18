# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p2g
family_name: p2g_rad_mult_frac
subskill_nodes: ["multiply_terms", "fractional_radical"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p2g】p2g_rad_mult_frac（level={}）".format(level)
    answer = "p2g_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p2g",
        "subskill_nodes": ["multiply_terms", "fractional_radical"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
