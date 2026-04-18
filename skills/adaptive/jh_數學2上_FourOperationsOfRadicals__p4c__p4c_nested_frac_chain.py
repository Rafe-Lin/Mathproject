# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p4c
family_name: p4c_nested_frac_chain
subskill_nodes: ["fractional_radical", "structure_isomorphism"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p4c】p4c_nested_frac_chain（level={}）".format(level)
    answer = "p4c_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p4c",
        "subskill_nodes": ["fractional_radical", "structure_isomorphism"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
