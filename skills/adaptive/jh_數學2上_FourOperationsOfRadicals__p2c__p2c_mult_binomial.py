# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學2上_FourOperationsOfRadicals
family_id: p2c
family_name: p2c_mult_binomial
subskill_nodes: ["multiply_terms", "distribute", "binomial_expand"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【p2c】p2c_mult_binomial（level={}）".format(level)
    answer = "p2c_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "p2c",
        "subskill_nodes": ["multiply_terms", "distribute", "binomial_expand"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
