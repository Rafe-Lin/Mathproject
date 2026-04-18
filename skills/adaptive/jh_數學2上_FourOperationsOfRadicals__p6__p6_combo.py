# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p6
family_name: p6_combo
subskill_nodes: ["simplify", "combine_like_terms", "multiply_terms", "divide_terms", "structure_isomorphism"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p6】p6_combo（level={}）".format(level)
    answer = "p6_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p6",
        "subskill_nodes": ["simplify", "combine_like_terms", "multiply_terms", "divide_terms", "structure_isomorphism"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
