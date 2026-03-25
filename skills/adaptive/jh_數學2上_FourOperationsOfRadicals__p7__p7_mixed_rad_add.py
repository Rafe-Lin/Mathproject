# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p7
family_name: p7_mixed_rad_add
subskill_nodes: ["mixed_number_radical", "combine_like_terms"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p7】p7_mixed_rad_add（level={}）".format(level)
    answer = "p7_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p7",
        "subskill_nodes": ["mixed_number_radical", "combine_like_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
