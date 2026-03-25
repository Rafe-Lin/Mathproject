# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p1b
family_name: p1b_add_sub_bracket
subskill_nodes: ["combine_like_terms", "bracket_scope"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p1b】p1b_add_sub_bracket（level={}）".format(level)
    answer = "p1b_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p1b",
        "subskill_nodes": ["combine_like_terms", "bracket_scope"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
