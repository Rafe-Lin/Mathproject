# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p1
family_name: p1_add_sub
subskill_nodes: ["combine_like_terms"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p1】p1_add_sub（level={}）".format(level)
    answer = "p1_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p1",
        "subskill_nodes": ["combine_like_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
