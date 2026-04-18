# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F3
family_name: Preserve-Value Fraction Invariance
subskill_nodes: ["preserve_value_invariance", "equivalent_fraction_scaling"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F3】Preserve-Value Fraction Invariance（level={}）".format(level)
    answer = "F3_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F3",
        "subskill_nodes": ["preserve_value_invariance", "equivalent_fraction_scaling"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
