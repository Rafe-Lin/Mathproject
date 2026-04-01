# -*- coding: utf-8 -*-
from __future__ import annotations

from fractions import Fraction
import math
import re
import unicodedata
from typing import Any


def _normalize_text(value: object) -> str:
    text = str(value or "").strip()
    return (
        text.replace(" ", "")
        .replace("$", "")
        .replace("\\left", "")
        .replace("\\right", "")
        .replace("{", "")
        .replace("}", "")
        .lower()
    )


def _to_halfwidth(text: str) -> str:
    return unicodedata.normalize("NFKC", text or "")


def _insert_implicit_multiplication(text: str) -> str:
    if not text:
        return text
    out = text
    out = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", out)
    out = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", out)
    out = re.sub(r"([a-zA-Z])([a-zA-Z])", r"\1*\2", out)
    out = re.sub(r"([a-zA-Z\)])\(", r"\1*(", out)
    out = re.sub(r"\)\(", r")*(", out)
    return out


def _repair_ambiguous_fraction_denominator(text: str) -> str:
    """
    Repair student shorthand like:
    - 5/3x  -> 5/(3*x)
    - 2/7ab -> 2/(7*a*b)
    Keep explicit forms unchanged:
    - 5/(3x)
    - (5/3)*x (or 5/3*x)
    """
    if not text:
        return text

    i = 0
    s = text
    out: list[str] = []
    n = len(s)
    stop_chars = set("+-*/^)")
    while i < n:
        ch = s[i]
        if ch != "/":
            out.append(ch)
            i += 1
            continue

        out.append("/")
        i += 1
        if i >= n:
            break
        if s[i] == "(":
            out.append("(")
            i += 1
            continue

        j = i
        while j < n and s[j] not in stop_chars:
            j += 1
        den = s[i:j]

        # Only repair bare denominator token that mixes digits and letters and has no explicit '*'.
        if den and ("*" not in den) and ("/" not in den) and any(c.isalpha() for c in den) and den[0].isdigit():
            repaired = _insert_implicit_multiplication(den)
            out.append(f"({repaired})")
        else:
            out.append(den)
        i = j

    return "".join(out)


def _normalize_math_text(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = _to_halfwidth(text)
    text = (
        text.replace(" ", "")
        .replace("$", "")
        .replace("\\left", "")
        .replace("\\right", "")
        .replace("{", "")
        .replace("}", "")
        .replace("?", "*")
        .replace("繩", "/")
        .lower()
    )
    text = _repair_ambiguous_fraction_denominator(text)
    text = _insert_implicit_multiplication(text)
    return text


def _as_fraction(value: str) -> Fraction | None:
    cleaned = value.replace("−", "-").replace("÷", "/")
    try:
        return Fraction(cleaned)
    except Exception:
        return None


def _as_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        frac = _as_fraction(value)
        return float(frac) if frac is not None else None


def _as_symbolic(value: str):
    try:
        from sympy import Rational, Symbol, sqrt, sympify
        from sympy.parsing.sympy_parser import (
            convert_xor,
            implicit_multiplication_application,
            standard_transformations,
            parse_expr,
        )

        text = _normalize_text(value)
        if not text:
            return None
        local_dict = {
            "x": Symbol("x"),
            "sqrt": sqrt,
            "pi": sympify("pi"),
        }
        transformations = standard_transformations + (
            convert_xor,
            implicit_multiplication_application,
        )
        return parse_expr(text, local_dict=local_dict, transformations=transformations, evaluate=True)
    except Exception:
        return None


def _as_symbolic_tolerant(value: object):
    try:
        from sympy import Symbol, sqrt, sympify
        from sympy.parsing.sympy_parser import (
            convert_xor,
            implicit_multiplication_application,
            standard_transformations,
            parse_expr,
        )

        text = _normalize_math_text(value)
        if not text:
            return None
        local_dict = {
            "x": Symbol("x"),
            "sqrt": sqrt,
            "pi": sympify("pi"),
        }
        transformations = standard_transformations + (
            convert_xor,
            implicit_multiplication_application,
        )
        return parse_expr(text, local_dict=local_dict, transformations=transformations, evaluate=True)
    except Exception:
        return None


def _symbolic_equal(lhs: object, rhs: object) -> bool:
    left = _as_symbolic_tolerant(lhs)
    right = _as_symbolic_tolerant(rhs)
    if left is not None and right is not None:
        try:
            from sympy import simplify
            return simplify(left - right) == 0
        except Exception:
            return False

    lnum = _as_float(_normalize_text(lhs))
    rnum = _as_float(_normalize_text(rhs))
    if lnum is not None and rnum is not None:
        return math.isclose(lnum, rnum, rel_tol=1e-9, abs_tol=1e-9)
    return False


def _normalize_qr_input(value: object) -> str:
    text = _to_halfwidth(str(value or "")).strip()
    text = (
        text.replace(" ", "")
        .replace("：", ":")
        .replace("，", ",")
        .replace("；", ";")
        .replace("商式", "商")
        .replace("餘式", "餘")
    )
    return text


def _parse_quotient_remainder(value: object) -> tuple[str, str] | None:
    text = _normalize_qr_input(value)
    if not text:
        return None

    # 1) q...r (supports with/without spaces): -3x-2 ... -1
    if "..." in text:
        parts = text.split("...", 1)
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0].strip(), parts[1].strip()

    # 2) labeled form: 商:-3x-2,餘:-1 / 商=-3x-2;餘=-1
    m = re.match(r"^商\s*[:=]\s*(.+?)\s*[,;]\s*餘\s*[:=]\s*(.+)$", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # 3) tuple form: (-3x-2,-1)
    if text.startswith("(") and text.endswith(")") and "," in text:
        body = text[1:-1]
        parts = body.split(",", 1)
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0].strip(), parts[1].strip()

    return None


def _extract_divisor_from_question(question_text: object) -> str:
    text = _normalize_qr_input(question_text)
    if not text:
        return ""
    # Handles forms like: (...)\div(3x) or (...)繩(3x)
    m = re.search(r"(?:\\div|繩)\(([^()]+)\)", text)
    if m:
        return m.group(1)
    return ""


def judge_answer_with_feedback(
    user_answer: object,
    correct_answer: object,
    *,
    question_text: object = "",
) -> dict[str, Any]:
    result: dict[str, Any] = {"is_correct": False, "feedback": ""}

    correct_qr = _parse_quotient_remainder(correct_answer)
    user_qr = _parse_quotient_remainder(user_answer)

    # F8/F9 style expected answer: compare quotient and remainder independently.
    if correct_qr:
        cq, cr = correct_qr
        if user_qr:
            uq, ur = user_qr
            result["is_correct"] = _symbolic_equal(uq, cq) and _symbolic_equal(ur, cr)
            return result

        result["is_correct"] = False
        result["feedback"] = "你的答案可能在數學上接近正確，但本題需用『商與餘數』格式表示，例如：3x+2 ... -3"
        return result

    result["is_correct"] = judge_answer(user_answer, correct_answer)
    return result


def judge_answer(user_answer: object, correct_answer: object) -> bool:
    user_text = _normalize_text(user_answer)
    correct_text = _normalize_text(correct_answer)

    if not user_text or not correct_text:
        return False
    if user_text == correct_text:
        return True

    user_num = _as_float(user_text)
    correct_num = _as_float(correct_text)
    if user_num is not None and correct_num is not None:
        return math.isclose(user_num, correct_num, rel_tol=1e-9, abs_tol=1e-9)

    user_frac = _as_fraction(user_text)
    correct_frac = _as_fraction(correct_text)
    if user_frac is not None and correct_frac is not None:
        return user_frac == correct_frac

    user_sym = _as_symbolic(user_text)
    correct_sym = _as_symbolic(correct_text)
    if user_sym is not None and correct_sym is not None:
        try:
            from sympy import simplify
            if simplify(user_sym - correct_sym) == 0:
                return True
        except Exception:
            pass

    # Tolerant symbolic fallback for formatting ambiguity in algebraic inputs.
    user_sym_tol = _as_symbolic_tolerant(user_answer)
    correct_sym_tol = _as_symbolic_tolerant(correct_answer)
    if user_sym_tol is not None and correct_sym_tol is not None:
        try:
            from sympy import simplify
            return simplify(user_sym_tol - correct_sym_tol) == 0
        except Exception:
            pass

    return False

