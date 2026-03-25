# -*- coding: utf-8 -*-
"""Auto-generated adaptive micro-skill stub.

skill_id: jh_數學1上_FourArithmeticOperationsOfNumbers
family_id: F10
family_name: Fraction Word Problems
subskill_nodes: ["remaining_amount", "container_weight", "before_after_ratio", "share_comparison"]
"""

from __future__ import annotations


def generate(level=1):
    question_text = "【F10】Fraction Word Problems（level={}）".format(level)
    answer = "F10_answer"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "F10",
        "subskill_nodes": ["remaining_amount", "container_weight", "before_after_ratio", "share_comparison"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
