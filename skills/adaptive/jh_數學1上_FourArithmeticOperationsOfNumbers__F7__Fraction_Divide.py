# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F7
family_name: Fraction Divide
subskill_nodes: ["divide", "mixed_numbers", "decimal_fraction_mixed_arithmetic"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F7】Fraction Divide（level={}）".format(level)
    answer = "F7_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F7",
        "subskill_nodes": ["divide", "mixed_numbers", "decimal_fraction_mixed_arithmetic"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
