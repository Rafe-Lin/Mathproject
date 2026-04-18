import random
from core.helpers import format_polynomial, validate_factor

def generate_factor_theorem_question():
    """動態生成一道「因式定理」的題目 (是/否)"""
    degree = random.choice([2, 3])
    k = random.randint(-3, 3)
    coeffs = []
    is_factor = random.choice([True, False])
    if degree == 2:
        a = random.randint(-3, 3)
        while a == 0:
            a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        if is_factor:
            c = -((a * (k**2)) + (b * k))
        else:
            c = random.randint(-9, 9)
            remainder = (a * (k**2)) + (b * k) + c
            while remainder == 0:
                c = random.randint(-9, 9)
                remainder = (a * (k**2)) + (b * k) + c
        coeffs = [a, b, c]
    elif degree == 3:
        a = random.randint(-2, 2)
        while a == 0:
            a = random.randint(-2, 2)
        b = random.randint(-3, 3)
        c = random.randint(-5, 5)
        if is_factor:
            d = -((a * (k**3)) + (b * (k**2)) + (c * k))
        else:
            d = random.randint(-9, 9)
            remainder = (a * (k**3)) + (b * (k**2)) + (c * k) + d
            while remainder == 0:
                d = random.randint(-9, 9)
                remainder = (a * (k**3)) + (b * (k**2)) + (c * k) + d
        coeffs = [a, b, c, d]
    poly_text = format_polynomial(coeffs)
    k_sign = "-" if k >= 0 else "+"
    k_abs = abs(k)
    divisor_text = "(x)" if k == 0 else f"(x {k_sign} {k_abs})"
    question_text = f"請問 {divisor_text} 是否為 f(x) = {poly_text} 的因式？ (請回答 '是' 或 '否')"
    correct_answer = "是" if is_factor else "否"
    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": validate_factor.__name__
    }
