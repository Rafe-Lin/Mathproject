import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「餘式定理 (除式為一次式)」的題目。
    level 1: 除式為 x-k
    level 2: 除式為 ax-b
    """
    f_coeffs = [random.randint(-5, 5) for _ in range(random.randint(3, 4))]
    f = np.poly1d(f_coeffs)

    if level == 1:
        k = random.randint(-5, 5)
        g_str = f"x - {k}" if k >= 0 else f"x + {abs(k)}"
        remainder = f(k)
    else: # level 2
        a, b = random.randint(2, 4), random.randint(-5, 5)
        g_str = f"{a}x - {b}" if b >= 0 else f"{a}x + {abs(b)}"
        remainder = f(b/a)

    question_text = f"請求出多項式 f(x) = {poly_to_string(f)} 除以 {g_str} 的餘式。"
    correct_answer = str(int(remainder)) if remainder == int(remainder) else f"{remainder.numerator}/{remainder.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}