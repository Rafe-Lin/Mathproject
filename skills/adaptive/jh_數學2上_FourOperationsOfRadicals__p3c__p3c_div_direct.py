# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p3c
family_name: p3c_div_direct
subskill_nodes: ["divide_terms"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p3c】p3c_div_direct（level={}）".format(level)
    answer = "p3c_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p3c",
        "subskill_nodes": ["divide_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
