# -*- coding: utf-8 -*-
from __future__ import annotations

import random
from typing import Callable

from .schema import CatalogEntry


def _latex_int(value: int) -> str:
    return f"({value})" if value < 0 else str(value)


def _pick_non_zero(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def _integers_i1(entry: CatalogEntry) -> dict:
    a = random.randint(-20, 20)
    b = _pick_non_zero(-12, 12)
    answer = a + b
    return {
        "question_text": f"請計算：$ {_latex_int(a)} + {_latex_int(b)} $",
        "latex": f"{_latex_int(a)} + {_latex_int(b)}",
        "answer": str(answer),
        "context_string": "先判斷正負號，再從左到右完成整數加減。",
    }


def _integers_i2(entry: CatalogEntry) -> dict:
    nums = [random.randint(-15, 15) for _ in range(3)]
    answer = sum(nums)
    latex = " ".join(
        [_latex_int(nums[0])] + [f"+ {_latex_int(n)}" if n >= 0 else f"- {_latex_int(abs(n))}" for n in nums[1:]]
    )
    return {
        "question_text": f"請計算下列各式的值：$ {latex} $",
        "latex": latex,
        "answer": str(answer),
        "context_string": "留意每一項的符號，依序把整數加減完成。",
    }


def _integers_i3(entry: CatalogEntry) -> dict:
    a = _pick_non_zero(-9, 9)
    b = _pick_non_zero(-9, 9)
    if random.choice([True, False]):
        answer = a * b
        latex = f"{_latex_int(a)} \\times {_latex_int(b)}"
    else:
        answer = a
        latex = f"{_latex_int(a * b)} \\div {_latex_int(b)}"
    return {
        "question_text": f"請計算：$ {latex} $",
        "latex": latex,
        "answer": str(answer),
        "context_string": "整數乘除先判斷正負，再計算數值。",
    }


def _integers_i4(entry: CatalogEntry) -> dict:
    a = random.randint(-12, 12)
    b = random.randint(-12, 12)
    c = _pick_non_zero(-6, 6)
    answer = a + b * c
    latex = f"{_latex_int(a)} + {_latex_int(b)} \\times {_latex_int(c)}"
    return {
        "question_text": f"請計算：$ {latex} $",
        "latex": latex,
        "answer": str(answer),
        "context_string": "這一題要先乘除，後加減。",
    }


def _integers_i5(entry: CatalogEntry) -> dict:
    a = random.randint(-12, 12)
    b = random.randint(-9, 9)
    c = random.randint(-9, 9)
    answer = (a + b) * c
    latex = f"\\left({_latex_int(a)} + {_latex_int(b)}\\right) \\times {_latex_int(c)}"
    return {
        "question_text": f"請計算：$ {latex} $",
        "latex": latex,
        "answer": str(answer),
        "context_string": "先算括號裡，再做外面的乘法。",
    }


def _integers_i6(entry: CatalogEntry) -> dict:
    a = random.randint(-15, 15)
    b = random.randint(-10, 10)
    answer = abs(a) + b
    latex = f"|{a}| + {_latex_int(b)}"
    return {
        "question_text": f"請計算：$ {latex} $",
        "latex": latex,
        "answer": str(answer),
        "context_string": "絕對值要先變成距離，也就是非負數。",
    }


def _integers_i7(entry: CatalogEntry) -> dict:
    inner = _pick_non_zero(-6, 6)
    multiplier = random.choice([2, 3, -2, -3])
    numerator = inner * multiplier
    bonus = random.randint(-5, 5)
    answer = numerator // multiplier + bonus
    latex = f"\\frac{{{_latex_int(numerator)}}}{{{_latex_int(multiplier)}}} + {_latex_int(bonus)}"
    return {
        "question_text": f"請計算：$ {latex} $",
        "latex": latex,
        "answer": str(answer),
        "context_string": "先把整除做完，再和後面的整數合併。",
    }


def _integers_i8(entry: CatalogEntry) -> dict:
    a = random.randint(-8, 8)
    b = _pick_non_zero(-5, 5)
    c = random.randint(-8, 8)
    answer = (a - b) * c + abs(b)
    latex = f"\\left({_latex_int(a)} - {_latex_int(b)}\\right) \\times {_latex_int(c)} + |{b}|"
    return {
        "question_text": f"請計算：$ {latex} $",
        "latex": latex,
        "answer": str(answer),
        "context_string": "這題是綜合結構題，先括號，再乘法，最後再加上絕對值。",
    }


INTEGER_GENERATORS: dict[str, Callable[[CatalogEntry], dict]] = {
    "I1": _integers_i1,
    "I2": _integers_i2,
    "I3": _integers_i3,
    "I4": _integers_i4,
    "I5": _integers_i5,
    "I6": _integers_i6,
    "I7": _integers_i7,
    "I8": _integers_i8,
}


def generate_micro_question(entry: CatalogEntry) -> dict | None:
    if entry.skill_id == "jh_數學1上_FourArithmeticOperationsOfIntegers":
        generator = INTEGER_GENERATORS.get(entry.family_id)
        if generator:
            payload = generator(entry)
            payload["family_id"] = entry.family_id
            payload["subskill_nodes"] = list(entry.subskill_nodes)
            return payload
    return None
