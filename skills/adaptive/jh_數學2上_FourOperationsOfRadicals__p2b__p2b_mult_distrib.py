# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p2b
family_name: p2b_mult_distrib
subskill_nodes: ["multiply_terms", "distribute"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p2b】p2b_mult_distrib（level={}）".format(level)
    answer = "p2b_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p2b",
        "subskill_nodes": ["multiply_terms", "distribute"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
