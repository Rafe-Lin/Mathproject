# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p3a
family_name: p3a_div_expr
subskill_nodes: ["divide_terms", "bracket_scope"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p3a】p3a_div_expr（level={}）".format(level)
    answer = "p3a_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p3a",
        "subskill_nodes": ["divide_terms", "bracket_scope"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
