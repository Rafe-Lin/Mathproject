import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「多項式除法原理」的題目。f(x) = g(x)q(x) + r(x)
    level 1: 給定 g, q, r, 求 f。
    level 2: 給定 f, g, r, 求 q。
    """
    q_coeffs = [random.randint(-3, 3) for _ in range(2)]
    g_coeffs = [random.randint(1, 3), random.randint(-3, 3)]
    r_coeffs = [random.randint(-5, 5)]
    q, g, r = np.poly1d(q_coeffs), np.poly1d(g_coeffs), np.poly1d(r_coeffs)
    f = g * q + r

    if level == 1:
        question_text = f"已知一多項式除以 ({poly_to_string(g)})，得商式為 ({poly_to_string(q)})，餘式為 {poly_to_string(r)}，求原多項式。"
        correct_answer = poly_to_string(f)
    else: # level 2
        question_text = f"已知多項式 ({poly_to_string(f)}) 除以 ({poly_to_string(g)})，得餘式為 {poly_to_string(r)}，求其商式。"
        correct_answer = poly_to_string(q)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²").replace("^3","³")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}