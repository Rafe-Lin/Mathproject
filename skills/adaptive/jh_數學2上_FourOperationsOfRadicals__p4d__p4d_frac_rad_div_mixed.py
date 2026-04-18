# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p4d
family_name: p4d_frac_rad_div_mixed
subskill_nodes: ["divide_terms", "conjugate_rationalize", "fractional_radical"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p4d】p4d_frac_rad_div_mixed（level={}）".format(level)
    answer = "p4d_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p4d",
        "subskill_nodes": ["divide_terms", "conjugate_rationalize", "fractional_radical"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
