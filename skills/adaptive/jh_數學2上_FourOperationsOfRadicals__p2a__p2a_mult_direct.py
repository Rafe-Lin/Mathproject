# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p2a
family_name: p2a_mult_direct
subskill_nodes: ["multiply_terms"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p2a】p2a_mult_direct（level={}）".format(level)
    answer = "p2a_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p2a",
        "subskill_nodes": ["multiply_terms"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
