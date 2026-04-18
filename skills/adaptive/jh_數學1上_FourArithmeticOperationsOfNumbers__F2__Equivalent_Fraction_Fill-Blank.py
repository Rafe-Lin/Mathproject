# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F2
family_name: Equivalent Fraction Fill-Blank
subskill_nodes: ["equivalent_fraction_scaling", "sign_normalization"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F2】Equivalent Fraction Fill-Blank（level={}）".format(level)
    answer = "F2_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F2",
        "subskill_nodes": ["equivalent_fraction_scaling", "sign_normalization"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
