# -*- coding: utf-8 -*-

from __future__ import annotations



import random

from fractions import Fraction

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





def _integers_i9(entry: CatalogEntry) -> dict:
    style = random.choice(["plain", "paren", "outside"])
    base = random.choice([2, 3, 4, 5])
    exponent = random.choice([2, 3])
    if style == "plain":
        question = f"請計算：$ {base}^{exponent} $"
        answer = str(base ** exponent)
        context = "先看底數與次方，再做乘方。"
    elif style == "paren":
        question = f"請計算：$ (-{base})^{exponent} $"
        answer = str(((-base) ** exponent))
        context = "負號在括號內，表示整個負數作為底數。"
    else:
        question = f"請計算：$ -{base}^{exponent} $"
        answer = str(-(base ** exponent))
        context = "負號在括號外，先做乘方，再套外面的負號。"
    return {
        "question_text": question,
        "latex": question,
        "answer": answer,
        "correct_answer": answer,
        "context_string": context,
    }


def _integers_i10(entry: CatalogEntry) -> dict:
    if random.choice([True, False]):
        a = random.choice([2, 3, 4, 5])
        b = random.choice([2, 3, 4])
        c = random.choice([2, 3, 4])
        question = f"請計算：$ (-{a}^2) \\div {a} - {b}^{c} $"
        answer = str((-(a ** 2)) // a - (b ** c))
    else:
        a = random.choice([2, 3, 4, 5, 8])
        b = random.choice([2, 3, 4])
        c = random.choice([2, 3, 4])
        question = f"請計算：$ {a} - 2^{b} \\times [10 + (-{c}^{2})] $"
        answer = str(a - (2 ** b) * (10 + (-(c ** 2))))
    return {
        "question_text": question,
        "latex": question,
        "answer": answer,
        "correct_answer": answer,
        "context_string": "乘方先算，再做乘除，最後加減。",
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

    "I9": _integers_i9,

    "I10": _integers_i10,

}





def _frac_latex(value: Fraction) -> str:

    if value.denominator == 1:

        return str(value.numerator)

    sign = '-' if value < 0 else ''

    value = abs(value)

    return f"{sign}\\frac{{{value.numerator}}}{{{value.denominator}}}"





def _frac_answer(value: Fraction) -> str:

    value = Fraction(value.numerator, value.denominator)

    if value.denominator == 1:

        return str(value.numerator)

    return f"{value.numerator}/{value.denominator}"





def _fraction_f1(entry: CatalogEntry) -> dict:

    base_num = random.randint(2, 9)
    base_den = random.randint(2, 9)
    factor = random.randint(2, 4)
    raw_num = base_num * factor
    raw_den = base_den * factor

    question = f"請化簡：$\\frac{{{raw_num}}}{{{raw_den}}}$"
    return {

        "question_text": question,

        "latex": f"\\frac{{{raw_num}}}{{{raw_den}}}",

        "answer": _frac_answer(Fraction(base_num, base_den)),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }

def _fraction_f2(entry: CatalogEntry) -> dict:

    base = Fraction(random.randint(1, 6), random.randint(2, 9))

    factor = random.randint(2, 5)

    target = base * factor

    question = (
        f"請在空格中填入等值分數："
        f"$\\square = \\frac{{{target.numerator}}}{{{target.denominator}}} \\div {factor}$"
    )
    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(base),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f3(entry: CatalogEntry) -> dict:

    base = Fraction(random.randint(1, 6), random.randint(2, 9))

    factor = random.randint(2, 5)

    question = f"請將下列分數擴大 {factor} 倍：${_frac_latex(base)}$"
    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(base * factor),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f4(entry: CatalogEntry) -> dict:

    left = Fraction(random.randint(1, 8), random.randint(2, 9))

    right = Fraction(random.randint(1, 8), random.randint(2, 9))

    if left == right:

        right += Fraction(1, 9)

    symbol = '>' if left > right else '<'

    question = f"請比較大小：${_frac_latex(left)}$ {symbol} ${_frac_latex(right)}$"
    return {

        "question_text": question,

        "latex": question,

        "answer": symbol,

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f5(entry: CatalogEntry) -> dict:

    den = random.choice([2, 3, 4, 5, 6, 8, 9, 10])

    a = Fraction(random.randint(1, den - 1), den)

    b = Fraction(random.randint(1, den - 1), den)

    if random.choice([True, False]):

        question = f"請計算下列分數的和：${_frac_latex(a)} + {_frac_latex(b)}$"
        ans = a + b

    else:

        question = f"請計算下列分數的差：${_frac_latex(a)} - {_frac_latex(b)}$"
        ans = a - b

    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(ans),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f6(entry: CatalogEntry) -> dict:

    a = Fraction(random.randint(1, 8), random.randint(2, 9))

    b = Fraction(random.randint(1, 8), random.randint(2, 9))

    question = f"請計算下列分數的積：${_frac_latex(a)} \\times {_frac_latex(b)}$"
    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(a * b),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f7(entry: CatalogEntry) -> dict:

    a = Fraction(random.randint(1, 8), random.randint(2, 9))

    b = Fraction(random.randint(1, 8), random.randint(2, 9))

    question = f"請計算下列分數的商：${_frac_latex(a)} \\div {_frac_latex(b)}$"
    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(a / b),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f8(entry: CatalogEntry) -> dict:

    a = Fraction(random.randint(2, 9), random.randint(2, 9))

    question = f"請寫出下列分數的倒數：${_frac_latex(a)}$"
    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(Fraction(a.denominator, a.numerator)),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f9(entry: CatalogEntry) -> dict:

    a = round(random.uniform(0.2, 2.0), 1)

    b = Fraction(random.randint(1, 8), random.randint(2, 9))

    if random.choice([True, False]):

        question = f"請計算下列小數與分數的和：${a} + {_frac_latex(b)}$"
        ans = Fraction(str(a)) + b

    else:

        question = f"請計算下列小數與分數的差：${a} - {_frac_latex(b)}$"
        ans = Fraction(str(a)) - b

    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(ans),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f10(entry: CatalogEntry) -> dict:

    whole = random.randint(2, 9)

    used = random.randint(1, whole - 1)

    left = Fraction(random.randint(1, 4), random.choice([2, 3, 4, 5, 6]))

    question = f"請計算：把一個整體平均分成 {whole} 份，先拿走其中 {used} 份，剩下的部分再加上 {_frac_latex(left)}。"
    ans = Fraction(whole - used, whole) + left

    return {

        "question_text": question,

        "latex": question,

        "answer": _frac_answer(ans),

        "family_id": entry.family_id,

        "subskill_nodes": list(entry.subskill_nodes),

    }





def _fraction_f11(entry: CatalogEntry) -> dict:
    if random.choice([True, False]):
        base = random.choice([2, 3, 4, 5, 6])
        p = random.randint(1, 5)
        q = random.randint(1, 5)
        question = f"請填空：$ {base}^{p} \\times {base}^{q} = {base}^{{\\square}} $"
    else:
        num = random.choice([1, 2, 3, 4, 5])
        den = random.choice([2, 3, 4, 5, 6])
        p = random.randint(1, 4)
        q = random.randint(1, 4)
        question = f"請填空：$ (\\frac{{{num}}}{{{den}}})^{p} \\times (\\frac{{{num}}}{{{den}}})^{q} = (\\frac{{{num}}}{{{den}}})^{{\\square}} $"
    answer = str(p + q)
    return {
        "question_text": question,
        "latex": question,
        "answer": answer,
        "correct_answer": answer,
        "context_string": "同底數相乘，指數相加。",
    }


def _fraction_f12(entry: CatalogEntry) -> dict:
    if random.choice([True, False]):
        base = random.choice([2, 3, 4, 5, 6])
        p = random.randint(1, 5)
        q = random.randint(1, 4)
        question = f"請填空：$ ({base}^{p})^{q} = {base}^{{\\square}} $"
    else:
        num = random.choice([1, 2, 3, 4, 5])
        den = random.choice([2, 3, 4, 5, 6])
        p = random.randint(1, 4)
        q = random.randint(1, 4)
        question = f"請填空：$ [(\\frac{{{num}}}{{{den}}})^{p}]^{q} = (\\frac{{{num}}}{{{den}}})^{{\\square}} $"
    answer = str(p * q)
    return {
        "question_text": question,
        "latex": question,
        "answer": answer,
        "correct_answer": answer,
        "context_string": "冪的冪，指數相乘。",
    }


def _fraction_f13(entry: CatalogEntry) -> dict:
    if random.choice([True, False]):
        a = random.choice([2, 3, 5, 7, 11])
        b = random.choice([2, 3, 5, 7, 11])
        n = random.randint(2, 5)
        question = f"請填空：$ ({a}\\times {b})^{n} = {a}^{{\\square}} \\times {b}^{{\\square}} $"
    else:
        a_num = random.choice([1, 2, 3, 4])
        a_den = random.choice([2, 3, 4, 5])
        b_num = random.choice([1, 2, 3, 4])
        b_den = random.choice([2, 3, 4, 5])
        n = random.randint(2, 4)
        question = (
            "請填空："
            f"$ (\\frac{{{a_num}}}{{{a_den}}}\\times\\frac{{{b_num}}}{{{b_den}}})^{n} "
            f"= (\\frac{{{a_num}}}{{{a_den}}})^{{\\square}}\\times(\\frac{{{b_num}}}{{{b_den}}})^{{\\square}} $"
        )
    answer = str(n)
    return {
        "question_text": question,
        "latex": question,
        "answer": answer,
        "correct_answer": answer,
        "context_string": "積的冪可以分配到每個因數上。",
    }


NUMBER_GENERATORS: dict[str, Callable[[CatalogEntry], dict]] = {

    "F1": _fraction_f1,

    "F2": _fraction_f2,

    "F3": _fraction_f3,

    "F4": _fraction_f4,

    "F5": _fraction_f5,

    "F6": _fraction_f6,

    "F7": _fraction_f7,

    "F8": _fraction_f8,

    "F9": _fraction_f9,

    "F10": _fraction_f10,

    "F11": _fraction_f11,

    "F12": _fraction_f12,

    "F13": _fraction_f13,

}





def generate_micro_question(entry: CatalogEntry) -> dict | None:

    skill_key = str(entry.skill_id)

    if 'FourArithmeticOperationsOfIntegers' in skill_key:

        generator = INTEGER_GENERATORS.get(entry.family_id)

        if generator:

            payload = generator(entry)

            payload['family_id'] = entry.family_id

            payload['subskill_nodes'] = list(entry.subskill_nodes)

            return payload

    if 'FourArithmeticOperationsOfNumbers' in skill_key:

        generator = NUMBER_GENERATORS.get(entry.family_id)

        if generator:

            payload = generator(entry)

            payload['family_id'] = entry.family_id

            payload['subskill_nodes'] = list(entry.subskill_nodes)

            return payload

    return None


# ===== New family-aware generators (polynomial / radicals) =====

def _sympy_text(expr) -> str:
    return str(expr).replace("**", "^").replace(" ", "")


def _poly_answer(expr) -> str:
    try:
        from sympy import expand
        return _sympy_text(expand(expr))
    except Exception:
        return _sympy_text(expr)


def _poly_generator(entry: CatalogEntry) -> dict | None:
    fid = entry.family_id

    def nz(low: int, high: int) -> int:
        value = 0
        while value == 0:
            value = random.randint(low, high)
        return value

    def format_linear(coef_x: int, const: int) -> str:
        parts: list[str] = []
        if coef_x != 0:
            if coef_x == 1:
                parts.append("x")
            elif coef_x == -1:
                parts.append("-x")
            else:
                parts.append(f"{coef_x}x")
        if const != 0:
            if parts:
                sign = "+" if const > 0 else "-"
                parts.append(f"{sign} {abs(const)}")
            else:
                parts.append(str(const))
        return " ".join(parts) if parts else "0"

    def format_factor_x_plus_const(k: int) -> str:
        if k == 0:
            return "x"
        if k > 0:
            return f"x + {k}"
        return f"x - {abs(k)}"

    def combine_add_expr(left: str, right: str) -> str:
        l = str(left or "").strip() or "0"
        r = str(right or "").strip() or "0"
        if l == "0":
            return r
        if r == "0":
            return l
        if r.startswith("-"):
            return f"{l} - {r[1:].strip()}"
        return f"{l} + {r}"

    def negate_expr(expr: str) -> str:
        clean = str(expr or "").strip() or "0"
        if clean == "0":
            return "0"
        if clean.startswith("-"):
            body = clean[1:].strip()
            if " " in body:
                return f"-({clean})"
            return body or "0"
        if " " in clean:
            return f"-({clean})"
        return f"-{clean}"

    def format_poly(coeffs: dict[int, int]) -> str:
        terms: list[str] = []
        for degree in sorted(coeffs.keys(), reverse=True):
            coef = int(coeffs.get(degree, 0) or 0)
            if coef == 0:
                continue
            if degree == 0:
                core = str(abs(coef))
            elif degree == 1:
                core = "x" if abs(coef) == 1 else f"{abs(coef)}x"
            else:
                core = f"x^{degree}" if abs(coef) == 1 else f"{abs(coef)}x^{degree}"
            sign = "-" if coef < 0 else "+"
            if not terms:
                terms.append(f"-{core}" if coef < 0 else core)
            else:
                terms.append(f"{sign} {core}")
        return " ".join(terms) if terms else "0"

    def poly_add(dst: dict[int, int], src: dict[int, int], scale: int = 1) -> None:
        for degree, coef in src.items():
            dst[degree] = int(dst.get(degree, 0) + scale * coef)
            if dst[degree] == 0:
                dst.pop(degree, None)

    def poly_mul(a: dict[int, int], b: dict[int, int]) -> dict[int, int]:
        out: dict[int, int] = {}
        for d1, c1 in a.items():
            for d2, c2 in b.items():
                out[d1 + d2] = int(out.get(d1 + d2, 0) + c1 * c2)
                if out[d1 + d2] == 0:
                    out.pop(d1 + d2, None)
        return out

    # Minimal no-dependency fallback for polynomial F1 so demo never drops to catalog_fallback.
    if fid == "F1":
        while True:
            a, c = [nz(-8, 8) for _ in range(2)]
            b, d = [random.randint(-9, 9) for _ in range(2)]
            coef_x = a + c
            const = b + d
            if coef_x == 0 and const == 0:
                continue
            break

        pieces = [f"{a}x"]
        if b != 0:
            pieces.append(f"{'+' if b > 0 else '-'} {abs(b)}")
        pieces.append(f"{'+' if c > 0 else '-'} {abs(c)}x")
        if d != 0:
            pieces.append(f"{'+' if d > 0 else '-'} {abs(d)}")

        answer = format_linear(coef_x, const)
        q = f"請化簡：{' '.join(pieces)}"
        exp = "先把 x 項合併，再把常數項合併，最後用 ax + b 形式寫出。"
        return {
            "question": q,
            "question_text": q,
            "latex": q,
            "answer": answer,
            "correct_answer": answer,
            "context_string": "先整理同類項，再合併。",
            "explanation": exp,
            "solution": exp,
            "family_id": entry.family_id,
            "subskill_nodes": list(entry.subskill_nodes),
        }

    # Minimal no-dependency fallback for polynomial F2 (nested add/sub).
    if fid == "F2":
        a, c = [nz(-7, 7) for _ in range(2)]
        b, d = [random.randint(-9, 9) for _ in range(2)]
        coef_x = (-a) + c
        const = (-b) - d
        if coef_x == 0 and const == 0:
            coef_x = 1

        def poly_linear(c1: int, c0: int) -> str:
            items: list[str] = []
            if c1 != 0:
                if c1 == 1:
                    items.append("x")
                elif c1 == -1:
                    items.append("-x")
                else:
                    items.append(f"{c1}x")
            if c0 != 0:
                if items:
                    items.append(f"{'+' if c0 > 0 else '-'} {abs(c0)}")
                else:
                    items.append(str(c0))
            return " ".join(items) if items else "0"

        answer = poly_linear(coef_x, const)
        left_inner = format_linear(a, b)
        right_inner = format_linear(c, -d)
        q_expr = combine_add_expr(negate_expr(left_inner), right_inner)
        q = f"請化簡：{q_expr}"
        exp = "先把負號分配進去，再合併同類項。"
        return {
            "question": q,
            "question_text": q,
            "latex": q,
            "answer": answer,
            "correct_answer": answer,
            "context_string": "先分配符號，再做同類項合併。",
            "explanation": exp,
            "solution": exp,
            "family_id": entry.family_id,
            "subskill_nodes": list(entry.subskill_nodes),
        }

    # Minimal no-dependency fallback for polynomial F5 (poly * poly).
    if fid == "F5":
        a, b = random.randint(-8, 8), random.randint(-8, 8)
        bx = a + b
        c0 = a * b

        def poly_quadratic(c2: int, c1: int, c0_: int) -> str:
            parts: list[str] = []
            if c2 != 0:
                if c2 == 1:
                    parts.append("x^2")
                elif c2 == -1:
                    parts.append("-x^2")
                else:
                    parts.append(f"{c2}x^2")
            if c1 != 0:
                if parts:
                    parts.append(f"{'+' if c1 > 0 else '-'} {abs(c1)}x")
                else:
                    parts.append(f"{c1}x")
            if c0_ != 0:
                if parts:
                    parts.append(f"{'+' if c0_ > 0 else '-'} {abs(c0_)}")
                else:
                    parts.append(str(c0_))
            return " ".join(parts) if parts else "0"

        answer = poly_quadratic(1, bx, c0)
        q = f"請展開：({format_factor_x_plus_const(a)})({format_factor_x_plus_const(b)})"
        exp = "用分配律把每一項都乘到，再合併同類項。"
        return {
            "question": q,
            "question_text": q,
            "latex": q,
            "answer": answer,
            "correct_answer": answer,
            "context_string": "每一項都要相乘，最後再整理。",
            "explanation": exp,
            "solution": exp,
            "family_id": entry.family_id,
            "subskill_nodes": list(entry.subskill_nodes),
        }

    try:
        from sympy import symbols, expand
    except Exception:
        return None

    x = symbols("x")

    def signed_term(coef: int, suffix: str = "") -> str:
        if coef == 0:
            return ""
        if coef == 1 and suffix:
            return suffix
        if coef == -1 and suffix:
            return f"-{suffix}"
        return f"{coef}{suffix}"

    def signed_const(num: int) -> str:
        if num == 0:
            return ""
        return f"+ {abs(num)}" if num >= 0 else f"- {abs(num)}"

    def format_term(coef: int, variable: str = "x") -> str:
        if coef == 0:
            return ""
        if coef == 1:
            return f"{variable}"
        if coef == -1:
            return f"-{variable}"
        return f"{coef}{variable}"

    def format_expression(terms: list[tuple[int, str]]) -> str:
        expr = ""
        for coef, term_str in terms:
            if coef == 0:
                continue
            clean_term = str(term_str or "").strip()
            if not clean_term:
                continue
            if clean_term in {"0", "+0", "-0", "+ 0", "- 0"}:
                continue
            clean_term = clean_term.replace("+-", "-").replace("+ -", "- ").strip()
            clean_term = clean_term.replace("(+", "(").replace("+)", ")")
            if coef >= 0:
                if expr:
                    expr += " + "
                expr += clean_term.lstrip("+").strip()
            else:
                if expr:
                    expr += " - "
                    expr += clean_term.replace("-", "", 1).strip() if clean_term.startswith("-") else clean_term
                else:
                    expr += "-"
                    expr += clean_term.replace("-", "", 1).strip() if clean_term.startswith("-") else clean_term
        return expr or "0"

    if fid == "F1":
        a, c = [nz(-8, 8) for _ in range(2)]
        b, d = [random.randint(-8, 8) for _ in range(2)]
        expr = (a * x + b) + (c * x + d)
        left = format_linear(a, b)
        right = format_linear(c, d)
        q = f"請化簡：${combine_add_expr(left, right)}$"
    elif fid == "F2":
        a, c = [nz(-6, 6) for _ in range(2)]
        b, d = [random.randint(-6, 6) for _ in range(2)]
        expr = -(a * x + b) + (c * x - d)
        left_inner = format_linear(a, b)
        right_inner = format_linear(c, -d)
        q = f"請化簡：${combine_add_expr(negate_expr(left_inner), right_inner)}$"
    elif fid == "F3":
        k, m, n = random.randint(2, 6), random.randint(-6, 6), nz(-6, 6)
        expr = k * (x + m) - n * x
        q = f"請化簡：${k}(x + {m}) - {n}x$"
    elif fid == "F4":
        a, b = random.randint(1, 6), random.randint(1, 6)
        p, qn = random.randint(1, 3), random.randint(0, 2)
        expr = (a * x**p) * (b * x**qn)
        q = f"請計算：${a}x^{p} \\times {b}x^{qn}$"
    elif fid == "F5":
        a, b = random.randint(-6, 6), random.randint(-6, 6)
        expr = expand((x + a) * (x + b))
        q = f"請展開：$({format_factor_x_plus_const(a)})({format_factor_x_plus_const(b)})$"
    elif fid == "F6":
        a = random.randint(1, 6)
        if random.choice([True, False]):
            expr = expand((x + a) ** 2)
            q = f"請展開：$(x + {a})^2$"
        else:
            expr = expand((x + a) * (x - a))
            q = f"請展開：$(x + {a})(x - {a})$"
    elif fid == "F7":
        # 單項式除法直接化簡
        divisor_coef = random.randint(1, 4)
        divisor_deg = random.randint(1, 2)
        q_a = nz(-8, 8)
        q_b = random.randint(-8, 8)
        quotient = {1: q_a, 0: q_b}
        divisor = {divisor_deg: divisor_coef}
        dividend = poly_mul(quotient, divisor)
        q = f"請化簡：$({format_poly(dividend)}) \\div ({format_poly(divisor)})$"
        answer = format_poly(quotient)
        exp = "各項係數分別相除，次方分別相減。"
        return {
            "question_text": q,
            "latex": q,
            "answer": answer,
            "correct_answer": answer,
            "context_string": "同底數相除時次方相減，係數要約分。",
            "explanation": exp,
            "solution": exp,
            "family_id": entry.family_id,
            "subskill_nodes": list(entry.subskill_nodes),
        }
    elif fid == "F8":
        # 單項式除法（商與餘數）
        divisor_coef = random.randint(1, 4)
        divisor_deg = random.randint(1, 2)
        quotient = {1: nz(-6, 6), 0: random.randint(-6, 6)}
        divisor = {divisor_deg: divisor_coef}
        remainder_degree = 0 if divisor_deg == 1 else random.randint(0, 1)
        remainder = {remainder_degree: nz(-5, 5)}
        dividend = poly_mul(quotient, divisor)
        poly_add(dividend, remainder, scale=1)
        q = f"請求商與餘數：$({format_poly(dividend)}) \\div ({format_poly(divisor)})$"
        answer = f"商：{format_poly(quotient)}，餘：{format_poly(remainder)}"
        exp = "先做單項式除法得到商，再檢查餘式次數是否小於除式次數。"
        return {
            "question_text": q,
            "latex": q,
            "answer": answer,
            "correct_answer": answer,
            "context_string": "用『被除式 = 除式×商 + 餘式』檢查結果。",
            "explanation": exp,
            "solution": exp,
            "family_id": entry.family_id,
            "subskill_nodes": list(entry.subskill_nodes),
        }
    elif fid == "F9":
        # 多項式長除法（商與餘數）
        divisor = {1: 1, 0: random.randint(-5, 5)}  # x + b
        quotient = {2: nz(-3, 3), 1: random.randint(-6, 6), 0: random.randint(-6, 6)}
        remainder = {0: random.randint(-4, 4)}
        dividend = poly_mul(divisor, quotient)
        poly_add(dividend, remainder, scale=1)
        q = f"請用多項式長除法求商與餘數：$({format_poly(dividend)}) \\div ({format_poly(divisor)})$"
        answer = f"商：{format_poly(quotient)}，餘：{format_poly(remainder)}"
        exp = "每一步都用最高次項相除，寫出商，再回乘相減。"
        return {
            "question_text": q,
            "latex": q,
            "answer": answer,
            "correct_answer": answer,
            "context_string": "長除法重點是『最高次對齊』與『回乘相減』。",
            "explanation": exp,
            "solution": exp,
            "family_id": entry.family_id,
            "subskill_nodes": list(entry.subskill_nodes),
        }
    elif fid == "F10":
        # 反推除法：已知除式、商、餘，求被除式
        divisor = {1: 1, 0: random.randint(-4, 4)}
        quotient = {1: nz(-5, 5), 0: random.randint(-5, 5)}
        remainder = {0: random.randint(-3, 3)}
        dividend = poly_mul(divisor, quotient)
        poly_add(dividend, remainder, scale=1)
        q = (
            "已知除式、商與餘數，求被除式："
            f"$\\text{{除式}}={format_poly(divisor)}$, "
            f"$\\text{{商}}={format_poly(quotient)}$, "
            f"$\\text{{餘}}={format_poly(remainder)}$。"
        )
        answer = format_poly(dividend)
        exp = "用公式『被除式 = 除式×商 + 餘』直接重建。"
        return {
            "question_text": q,
            "latex": q,
            "answer": answer,
            "correct_answer": answer,
            "context_string": "先做除式乘商，再加上餘數。",
            "explanation": exp,
            "solution": exp,
            "family_id": entry.family_id,
            "subskill_nodes": list(entry.subskill_nodes),
        }
    elif fid == "F11":
        a, b, c = random.randint(1, 5), random.randint(1, 5), random.randint(-5, 5)
        expr = expand((x + a) ** 2 + (x + b) * (x - b) + c * x)
        linear_term = format_term(c, "x")
        display_expr = format_expression([
            (1, f"(x + {a})^2"),
            (1, f"(x + {b})(x - {b})"),
            (c, linear_term),
        ])
        q = f"請化簡：${display_expr}$"
    elif fid == "F12":
        w, h = random.randint(2, 8), random.randint(2, 8)
        expr = expand((x + w) * (x + h))
        q = f"一個長方形的長是 x+{w}，寬是 x+{h}，面積是多少？"
    elif fid == "F13":
        a, b, c = random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)
        expr = expand((x + a) * (x + b) + (x + c))
        q = f"請化簡：$(x + {a})(x + {b}) + (x + {c})$"
    else:
        return None

    return {
        "question_text": q,
        "latex": q,
        "answer": _poly_answer(expr),
        "family_id": entry.family_id,
        "subskill_nodes": list(entry.subskill_nodes),
    }


def _radical_answer(expr) -> str:
    try:
        from sympy import simplify
        return _sympy_text(simplify(expr))
    except Exception:
        return _sympy_text(expr)


def _radical_rationalized(expr) -> str:
    try:
        from sympy import radsimp
        return _sympy_text(radsimp(expr))
    except Exception:
        return _radical_answer(expr)


def _radical_generator(entry: CatalogEntry) -> dict | None:
    try:
        from sympy import Rational, sqrt, symbols, expand
    except Exception:
        return None

    fid = entry.family_id
    x = symbols("x")

    def pos_choice() -> int:
        return random.choice([2, 3, 5, 6, 7, 8, 10, 12, 15, 18])

    if fid == "p0":
        n = random.choice([4, 8, 9, 12, 18, 20, 24, 27, 32, 50])
        expr = sqrt(n)
        q = f"請化簡：$\\sqrt{{{n}}}$"
    elif fid in {"p1", "p1b", "p1c"}:
        a = pos_choice()
        if fid == "p1":
            expr = 2 * sqrt(a) + 3 * sqrt(a)
            q = f"請化簡：$2\\sqrt{{{a}}} + 3\\sqrt{{{a}}}$"
        elif fid == "p1b":
            expr = 4 * sqrt(a) - sqrt(a)
            q = f"請化簡：$4\\sqrt{{{a}}} - \\sqrt{{{a}}}$"
        else:
            expr = Rational(1, 2) * sqrt(a) + Rational(3, 2) * sqrt(a)
            q = f"請化簡：$\\frac{{1}}{{2}}\\sqrt{{{a}}} + \\frac{{3}}{{2}}\\sqrt{{{a}}}$"
    elif fid in {"p2a", "p2f", "p2g", "p2h"}:
        a, b = pos_choice(), pos_choice()
        coeff = random.randint(2, 5)
        if fid == "p2a":
            expr = sqrt(a) * sqrt(b)
            q = f"請計算：$\\sqrt{{{a}}} \\times \\sqrt{{{b}}}$"
        elif fid == "p2f":
            expr = coeff * sqrt(a) * 2
            q = f"請計算：${coeff}\\sqrt{{{a}}} \\times 2$"
        elif fid == "p2g":
            expr = sqrt(a) * Rational(2, 3)
            q = f"請計算：$\\sqrt{{{a}}} \\times \\frac{{2}}{{3}}$"
        else:
            expr = Rational(2, 3) * sqrt(a)
            q = f"請計算：$\\frac{{2}}{{3}} \\times \\sqrt{{{a}}}$"
    elif fid in {"p2b", "p2c", "p2d", "p2e"}:
        a, b = pos_choice(), pos_choice()
        if fid == "p2b":
            expr = sqrt(a) * (3 + sqrt(b))
            q = f"請展開：$\\sqrt{{{a}}}(3 + \\sqrt{{{b}}})$"
        elif fid == "p2c":
            expr = (sqrt(a) + sqrt(b)) ** 2
            q = f"請展開：$(\\sqrt{{{a}}} + \\sqrt{{{b}}})^2$"
        elif fid == "p2d":
            expr = (sqrt(a) + sqrt(b)) * (sqrt(a) - sqrt(b))
            q = f"請展開：$(\\sqrt{{{a}}} + \\sqrt{{{b}}})(\\sqrt{{{a}}} - \\sqrt{{{b}}})$"
        else:
            expr = (sqrt(a) + sqrt(b)) * (sqrt(a) - sqrt(b))
            q = f"請化簡：$(\\sqrt{{{a}}} + \\sqrt{{{b}}})(\\sqrt{{{a}}} - \\sqrt{{{b}}})$"
    elif fid in {"p3a", "p3b", "p3c"}:
        a = pos_choice()
        if fid == "p3a":
            expr = sqrt(a * 4) / sqrt(4)
            q = f"請化簡：$\\frac{{\\sqrt{{{a*4}}}}}{{\\sqrt{{4}}}}$"
        elif fid == "p3b":
            expr = sqrt(a * 9) / 3
            q = f"請化簡：$\\frac{{\\sqrt{{{a*9}}}}}{{3}}$"
        else:
            expr = Rational(3, 1) * sqrt(a) / sqrt(a)
            q = f"請化簡：$\\frac{{3\\sqrt{{{a}}}}}{{\\sqrt{{{a}}}}}$"
    elif fid in {"p4", "p4b", "p4c", "p4d"}:
        a = pos_choice()
        if fid == "p4":
            expr = sqrt(a) / 2 * 4
            q = f"請計算：$\\frac{{\\sqrt{{{a}}}}}{{2}} \\times 4$"
        elif fid == "p4b":
            expr = Rational(3, 1) * sqrt(a) / sqrt(a * 4)
            q = f"請化簡：$\\frac{{3\\sqrt{{{a}}}}}{{\\sqrt{{{a*4}}}}}$"
        elif fid == "p4c":
            expr = Rational(1, 1) / sqrt(a) * sqrt(a)
            q = f"請化簡：$\\frac{{1}}{{\\sqrt{{{a}}}}} \\times \\sqrt{{{a}}}$"
        else:
            expr = Rational(2, 1) / sqrt(a) / sqrt(a * 4)
            q = f"請化簡：$\\frac{{2}}{{\\sqrt{{{a}}}}} \\div \\sqrt{{{a*4}}}$"
    elif fid in {"p5a", "p5b"}:
        a, b = pos_choice(), pos_choice()
        if fid == "p5a":
            expr = 1 / (2 + sqrt(a))
            q = f"請有理化：$\\frac{{1}}{{2+\\sqrt{{{a}}}}}$"
        else:
            expr = 1 / (sqrt(a) + sqrt(b))
            q = f"請有理化：$\\frac{{1}}{{\\sqrt{{{a}}}+\\sqrt{{{b}}}}}$"
    elif fid in {"p6", "p7"}:
        a, b = pos_choice(), pos_choice()
        if fid == "p6":
            expr = 2 * sqrt(a) + sqrt(a * 4) + sqrt(b)
            q = f"請化簡：$2\\sqrt{{{a}}} + \\sqrt{{{a*4}}} + \\sqrt{{{b}}}$"
        else:
            expr = sqrt(a) + sqrt(a * 4) + sqrt(b)
            q = f"請化簡：$\\sqrt{{{a}}} + \\sqrt{{{a*4}}} + \\sqrt{{{b}}}$"
    else:
        return None

    return {
        "question_text": q,
        "latex": q,
        "answer": _radical_rationalized(expr) if fid in {"p5a", "p5b"} else _radical_answer(expr),
        "family_id": entry.family_id,
        "subskill_nodes": list(entry.subskill_nodes),
    }


def generate_micro_question(entry: CatalogEntry) -> dict | None:
    skill_key = str(entry.skill_id)
    if 'FourArithmeticOperationsOfIntegers' in skill_key:
        generator = INTEGER_GENERATORS.get(entry.family_id)
        if generator:
            payload = generator(entry)
            payload['family_id'] = entry.family_id
            payload['subskill_nodes'] = list(entry.subskill_nodes)
            return payload
    if 'FourArithmeticOperationsOfNumbers' in skill_key:
        generator = NUMBER_GENERATORS.get(entry.family_id)
        if generator:
            payload = generator(entry)
            payload['family_id'] = entry.family_id
            payload['subskill_nodes'] = list(entry.subskill_nodes)
            return payload
    if 'FourArithmeticOperationsOfPolynomial' in skill_key:
        payload = _poly_generator(entry)
        if payload:
            return payload
    if 'FourOperationsOfRadicals' in skill_key:
        payload = _radical_generator(entry)
        if payload:
            return payload
    return None


def has_micro_generator(entry: CatalogEntry) -> bool:
    skill_key = str(entry.skill_id)
    fid = str(entry.family_id)
    if 'FourArithmeticOperationsOfIntegers' in skill_key:
        return fid in INTEGER_GENERATORS
    if 'FourArithmeticOperationsOfNumbers' in skill_key:
        return fid in NUMBER_GENERATORS
    if 'FourArithmeticOperationsOfPolynomial' in skill_key:
        return fid in {"F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"}
    if 'FourOperationsOfRadicals' in skill_key:
        return fid in {"p0", "p1", "p1b", "p1c", "p2a", "p2b", "p2c", "p2d", "p2e", "p2f", "p2g", "p2h", "p3a", "p3b", "p3c", "p4", "p4b", "p4c", "p4d", "p5a", "p5b", "p6", "p7"}
    return False
