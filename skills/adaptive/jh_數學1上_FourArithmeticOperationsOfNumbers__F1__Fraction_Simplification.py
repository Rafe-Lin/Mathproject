# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F1
family_name: Fraction Simplification
subskill_nodes: ["proper_improper_fraction", "mixed_numbers", "sign_normalization", "simplest_form_reduction"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F1】Fraction Simplification（level={}）".format(level)
    answer = "F1_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F1",
        "subskill_nodes": ["proper_improper_fraction", "mixed_numbers", "sign_normalization", "simplest_form_reduction"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
