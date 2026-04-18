import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「多項式加減法」的題目。
    level 1: 二次多項式。
    level 2: 三次多項式。
    """
    deg = 2 if level == 1 else 3
    f_coeffs = [random.randint(-5, 5) for _ in range(deg + 1)]
    g_coeffs = [random.randint(-5, 5) for _ in range(deg + 1)]
    f = np.poly1d(f_coeffs)
    g = np.poly1d(g_coeffs)
    
    op = random.choice(['+', '-'])
    question_text = f"請計算 ({poly_to_string(f)}) {op} ({poly_to_string(g)})"
    
    ans_poly = f + g if op == '+' else f - g
    correct_answer = poly_to_string(ans_poly)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²").replace("^3","³")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}