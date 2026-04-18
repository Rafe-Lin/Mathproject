# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p0
family_name: p0_simplify
subskill_nodes: ["simplify"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p0】p0_simplify（level={}）".format(level)
    answer = "p0_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p0",
        "subskill_nodes": ["simplify"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
