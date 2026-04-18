import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「多項式乘法」的題目。
    level 1: 一次式 * 一次式 或 一次式 * 二次式。
    level 2: 二次式 * 二次式。
    """
    if level == 1:
        f_coeffs = [random.randint(-3, 3) for _ in range(2)]
        g_coeffs = [random.randint(-3, 3) for _ in range(random.choice([2, 3]))]
    else: # level 2
        f_coeffs = [random.randint(-3, 3) for _ in range(3)]
        g_coeffs = [random.randint(-3, 3) for _ in range(3)]
    f = np.poly1d(f_coeffs)
    g = np.poly1d(g_coeffs)
    
    question_text = f"請計算 ({poly_to_string(f)}) * ({poly_to_string(g)})"
    correct_answer = poly_to_string(f * g)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²").replace("^3","³").replace("^4","⁴")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}