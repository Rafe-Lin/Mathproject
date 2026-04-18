# \多項式\餘式定理 (除式 x-a)
import random
import numpy as np
from .utils import poly_to_string, check_answer

def generate(level=1):
    """
    生成一道「餘式定理 (除式 x-a)」的題目。
    """
    # 構造一個多項式
    coeffs = [random.randint(-5, 5) for _ in range(random.randint(3, 4))]
    while coeffs[0] == 0: coeffs[0] = random.randint(1, 5)
    poly = np.poly1d(coeffs)
    poly_str = poly_to_string(poly)
    
    # 構造除式 x-a
    a = random.randint(-5, 5)
    divisor_str = f"x - {a}" if a >= 0 else f"x + {abs(a)}"
    
    question_text = f"請求出多項式 f(x) = {poly_str} 除以 {divisor_str} 的餘式。"
    correct_answer = str(np.polyval(poly, a))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')