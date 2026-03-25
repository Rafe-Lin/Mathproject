# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p1c
family_name: p1c_mixed_frac_rad_add_sub
subskill_nodes: ["combine_like_terms", "fractional_radical"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p1c】p1c_mixed_frac_rad_add_sub（level={}）".format(level)
    answer = "p1c_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p1c",
        "subskill_nodes": ["combine_like_terms", "fractional_radical"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
