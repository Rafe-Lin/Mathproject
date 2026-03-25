# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p4b
family_name: p4b_frac_rad_div
subskill_nodes: ["divide_terms", "conjugate_rationalize"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p4b】p4b_frac_rad_div（level={}）".format(level)
    answer = "p4b_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p4b",
        "subskill_nodes": ["divide_terms", "conjugate_rationalize"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
