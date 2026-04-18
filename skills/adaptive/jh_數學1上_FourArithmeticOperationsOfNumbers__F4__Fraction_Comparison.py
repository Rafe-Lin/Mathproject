# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F4
family_name: Fraction Comparison
subskill_nodes: ["positive_fraction_comparison", "negative_fraction_comparison", "mixed_number_comparison"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F4】Fraction Comparison（level={}）".format(level)
    answer = "F4_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F4",
        "subskill_nodes": ["positive_fraction_comparison", "negative_fraction_comparison", "mixed_number_comparison"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
