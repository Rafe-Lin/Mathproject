# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p5a
family_name: p5a_conjugate_int
subskill_nodes: ["divide_terms", "conjugate_rationalize"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p5a】p5a_conjugate_int（level={}）".format(level)
    answer = "p5a_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p5a",
        "subskill_nodes": ["divide_terms", "conjugate_rationalize"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
