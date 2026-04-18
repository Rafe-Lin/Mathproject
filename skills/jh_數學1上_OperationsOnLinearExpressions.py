# -*- coding: utf-8 -*-
from __future__ import annotations

import random
from fractions import Fraction
from typing import Callable

SKILL_ID = "jh_數學1上_OperationsOnLinearExpressions"

FAMILY_REGISTRY = {
    "L1": {"name": "linear_flat_mul_div", "label": "單項乘除轉寫"},
    "L2": {"name": "linear_combine_like_terms", "label": "同類項合併"},
    "L3": {"name": "linear_flat_simplify_with_constants", "label": "平面代數式化簡"},
    "L4": {"name": "linear_outer_minus_scope", "label": "括號前負號整包變號"},
    "L5": {"name": "linear_monomial_distribution", "label": "單項分配到括號"},
    "L6": {"name": "linear_nested_simplify", "label": "多括號綜合化簡"},
    "L7": {"name": "linear_fraction_expression_simplify", "label": "分式代數式化簡"},
}

FAMILY_SUBSKILLS = {
    "L1": ["coefficient_sign_handling"],
    "L2": ["like_term_combination"],
    "L3": ["term_collection_with_constants", "like_term_combination"],
    "L4": ["outer_minus_scope"],
    "L5": ["monomial_distribution", "coefficient_sign_handling"],
    "L6": ["nested_bracket_scope", "structure_isomorphism", "like_term_combination"],
    "L7": ["fractional_expression_simplification", "nested_bracket_scope"],
}


def _nz(low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def _frac(value: Fraction | int) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(value, 1)


def _fmt_num(value: Fraction | int) -> str:
    value = _frac(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _fmt_coeff_var(coeff: Fraction | int, var: str = "x") -> str:
    coeff = _frac(coeff)
    if coeff == 0:
        return "0"
    if coeff == 1:
        return var
    if coeff == -1:
        return f"-{var}"
    if coeff.denominator == 1:
        return f"{coeff.numerator}{var}"
    return f"{coeff.numerator}/{coeff.denominator}{var}"


def _fmt_linear(ax: Fraction | int, b: Fraction | int, var: str = "x") -> str:
    ax = _frac(ax)
    b = _frac(b)
    terms: list[str] = []
    if ax != 0:
        terms.append(_fmt_coeff_var(ax, var))
    if b != 0:
        if terms and b > 0:
            terms.append(f"+ {_fmt_num(b)}")
        elif terms and b < 0:
            terms.append(f"- {_fmt_num(abs(b))}")
        else:
            terms.append(_fmt_num(b))
    return " ".join(terms) if terms else "0"


def _normalize(text: str) -> str:
    raw = str(text or "").strip().lower()
    return raw.replace(" ", "").replace("＋", "+").replace("－", "-").replace("−", "-")


def _wrap_payload(question_text: str, correct_answer: str, explanation: str) -> dict:
    return {
        "question": question_text,
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation,
    }


def _gen_L1() -> dict:
    var = random.choice(["x", "y", "a", "b", "c"])
    c1 = Fraction(_nz(-12, 12), random.choice([1, 1, 2, 3, 4]))
    c2 = Fraction(_nz(-10, 10), random.choice([1, 1, 2, 3, 4]))
    if random.random() < 0.5:
        expr = f"({_fmt_coeff_var(c1, var)}) × ({_fmt_num(c2)})"
        ans = _fmt_coeff_var(c1 * c2, var)
    else:
        expr = f"({_fmt_coeff_var(c1, var)}) ÷ ({_fmt_num(c2)})"
        ans = _fmt_coeff_var(c1 / c2, var)
    return _wrap_payload(
        f"化簡：{expr}",
        ans,
        "先算係數的乘除，再保留變數與符號。",
    )


def _gen_L2() -> dict:
    var = random.choice(["x", "y", "a", "b"])
    left = Fraction(_nz(-16, 16), random.choice([1, 1, 1, 2, 3, 4, 5]))
    right = Fraction(_nz(-16, 16), random.choice([1, 1, 2, 3, 4, 5]))
    if random.random() < 0.5:
        expr = f"{_fmt_coeff_var(left, var)} + {_fmt_coeff_var(right, var)}"
    else:
        expr = f"{_fmt_coeff_var(left, var)} - ({_fmt_coeff_var(-right, var)})"
    ans = _fmt_coeff_var(left + right, var)
    return _wrap_payload(
        f"合併同類項：{expr}",
        ans,
        "先確認是同一個變數，再把係數相加減。",
    )


def _gen_L3() -> dict:
    var = random.choice(["x", "y", "a"])
    a, b, c, d = [random.randint(-14, 14) for _ in range(4)]
    if a == 0 and c == 0:
        a = _nz(-8, 8)
    expr = f"{_fmt_coeff_var(a, var)} + {b} + {_fmt_coeff_var(c, var)} + {d}"
    ans = _fmt_linear(a + c, b + d, var)
    return _wrap_payload(
        f"化簡：{expr}",
        ans,
        "把代數項和常數項分開整理，再合併。",
    )


def _gen_L4() -> dict:
    var = "x"
    a = _nz(-10, 10)
    b = random.randint(-12, 12)
    inner = f"{_fmt_coeff_var(a, var)} {'+' if b >= 0 else '-'} {abs(b)}"
    expr = f"-({inner})"
    ans = _fmt_linear(-a, -b, var)
    return _wrap_payload(
        f"去括號並化簡：{expr}",
        ans,
        "外層負號要乘進括號內每一項，全部變號。",
    )


def _gen_L5() -> dict:
    var = "x"
    k = _nz(-8, 8)
    a = _nz(-10, 10)
    b = random.randint(-15, 15)
    inner = f"{_fmt_coeff_var(a, var)} {'+' if b >= 0 else '-'} {abs(b)}"
    if random.random() < 0.5:
        expr = f"{k}({inner})"
    else:
        expr = f"({inner}) × ({k})"
    ans = _fmt_linear(k * a, k * b, var)
    return _wrap_payload(
        f"展開並化簡：{expr}",
        ans,
        "係數要分配到括號每一項，注意正負號。",
    )


def _gen_L6() -> dict:
    var = "x"
    if random.random() < 0.5:
        a, b = _nz(-6, 6), random.randint(-8, 8)
        c, d = _nz(-6, 6), random.randint(-8, 8)
        k, m = _nz(-6, 6), _nz(-6, 6)
        expr = (
            f"{k}({_fmt_coeff_var(a, var)} {'+' if b >= 0 else '-'} {abs(b)})"
            f" + {m}({_fmt_coeff_var(c, var)} {'+' if d >= 0 else '-'} {abs(d)})"
        )
        ans = _fmt_linear(k * a + m * c, k * b + m * d, var)
    else:
        p = _nz(-10, 10)
        a, b = _nz(-6, 6), random.randint(-8, 8)
        c, d = _nz(-6, 6), random.randint(-8, 8)
        expr = f"{p}{var} - 2[{_fmt_coeff_var(a, var)} - ({_fmt_coeff_var(c, var)} {'+' if d >= 0 else '-'} {abs(d)})]"
        ans = _fmt_linear(p - 2 * (a - c), 2 * d, var)
    return _wrap_payload(
        f"化簡：{expr}",
        ans,
        "先處理最內層括號，再逐層展開並合併同類項。",
    )


def _gen_L7() -> dict:
    var = "x"
    a, b, c, d = [random.randint(-9, 9) for _ in range(4)]
    den1, den2 = random.choice([2, 3, 4, 5, 6]), random.choice([2, 3, 4, 5, 6])
    expr = (
        f"({_fmt_coeff_var(a, var)} {'+' if b >= 0 else '-'} {abs(b)})/{den1}"
        f" - ({_fmt_coeff_var(c, var)} {'+' if d >= 0 else '-'} {abs(d)})/{den2}"
    )
    coeff = Fraction(a, den1) - Fraction(c, den2)
    const = Fraction(b, den1) - Fraction(d, den2)
    ans = _fmt_linear(coeff, const, var)
    return _wrap_payload(
        f"分式代數式化簡：{expr}",
        ans,
        "先處理分式係數，再合併同類項與常數項。",
    )


GEN_BY_FAMILY: dict[str, Callable[[], dict]] = {
    "L1": _gen_L1,
    "L2": _gen_L2,
    "L3": _gen_L3,
    "L4": _gen_L4,
    "L5": _gen_L5,
    "L6": _gen_L6,
    "L7": _gen_L7,
}


def _family_for_level(level: int) -> str:
    if level <= 1:
        return random.choice(["L1", "L2", "L3"])
    if level == 2:
        return random.choice(["L2", "L4", "L5"])
    return random.choice(["L4", "L5", "L6", "L7"])


def generate(level=1, **kwargs):
    family_id = str(kwargs.get("family_id") or kwargs.get("target_family_id") or "").strip().upper()
    if family_id not in GEN_BY_FAMILY:
        family_id = _family_for_level(int(level or 1))
    payload = dict(GEN_BY_FAMILY[family_id]())
    payload.update(
        {
            "family_id": family_id,
            "family": family_id,
            "family_name": FAMILY_REGISTRY[family_id]["name"],
            "family_label": FAMILY_REGISTRY[family_id]["label"],
            "skill_id": SKILL_ID,
            "subskill_nodes": list(FAMILY_SUBSKILLS.get(family_id, [])),
            "mode": int(level or 1),
        }
    )
    return payload


def check(user_answer, correct_answer):
    return _normalize(user_answer) == _normalize(correct_answer)
