# -*- coding: utf-8 -*-
from __future__ import annotations

import random
from typing import Callable


def _fmt_int(value: int) -> str:
    return str(value)


def _build_case_outer_minus_simple() -> tuple[str, int, str]:
    a = random.randint(2, 12)
    b = random.randint(-9, 9)
    expression = f"-({_fmt_int(a)} + {_fmt_int(b)})"
    answer = -(a + b)
    explanation = "括號前有負號，括號內每一項先保持原值，最後整包取相反數。"
    return expression, answer, explanation


def _build_case_outer_minus_with_negative() -> tuple[str, int, str]:
    a = random.randint(-12, -2)
    b = random.randint(2, 12)
    expression = f"-({_fmt_int(a)} + {_fmt_int(b)})"
    answer = -(a + b)
    explanation = "先算括號內和，再乘上 -1；等價於每一項都變號。"
    return expression, answer, explanation


def _build_case_outer_minus_plus_const() -> tuple[str, int, str]:
    a = random.randint(2, 12)
    b = random.randint(1, 9)
    c = random.randint(-9, 9)
    expression = f"-({_fmt_int(a)} - {_fmt_int(b)}) + {_fmt_int(c)}"
    answer = -(a - b) + c
    explanation = "先處理外層負號作用到整個括號，再與外部常數相加減。"
    return expression, answer, explanation


def _build_case_double_negative_brackets() -> tuple[str, int, str]:
    a = random.randint(3, 12)
    b = random.randint(1, 9)
    c = random.randint(-9, 9)
    d = random.randint(-9, 9)
    expression = f"-(-{_fmt_int(a)} + {_fmt_int(b)}) + ({_fmt_int(c)} - {_fmt_int(d)})"
    answer = -(-a + b) + (c - d)
    explanation = "外層負號會讓括號內每一項變號，再與第二個括號結果合併。"
    return expression, answer, explanation


def _build_case_given_style() -> tuple[str, int, str]:
    expression = "-(-6 + 8) + (-6 - 6)"
    answer = -(-6 + 8) + (-6 - 6)
    explanation = "先把第一個括號整包變號：-(-6+8)=6-8，再與第二括號結果相加。"
    return expression, answer, explanation


_CASE_BUILDERS: list[Callable[[], tuple[str, int, str]]] = [
    _build_case_outer_minus_simple,
    _build_case_outer_minus_with_negative,
    _build_case_outer_minus_plus_const,
    _build_case_double_negative_brackets,
    _build_case_given_style,
]


def generate(level: int = 1) -> dict:
    builder = random.choice(_CASE_BUILDERS)
    expression, answer_value, explanation = builder()
    question_text = f"計算：{expression}"
    answer = str(answer_value)
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "correct_answer": answer,
        "explanation": explanation,
        "solution": explanation,
        "context_string": "重點：括號前負號會作用到整個括號，每一項都要變號。",
        "family_id": "I5",
        "family": "I5",
        "family_name": "int_bracket_mixed",
        "subskill_nodes": ["sign_handling", "parentheses", "mixed_ops"],
    }


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
