import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「餘式定理 (除式為二次式)」的題目。
    level 1: 除式可分解為 (x-a)(x-b)，a, b 為整數。
    level 2: 綜合應用。
    """
    f_coeffs = [random.randint(-3, 3) for _ in range(4)]
    f = np.poly1d(f_coeffs)
    
    a, b = random.randint(-3, 3), random.randint(-3, 3)
    while a == b: b = random.randint(-3, 3)
    g = np.poly1d([1, -(a+b), a*b]) # g(x) = (x-a)(x-b)
    
    # f(x) = g(x)q(x) + r(x), r(x) = cx+d
    # f(a) = ca+d, f(b) = cb+d
    fa, fb = f(a), f(b)
    # 解連立: c = (fa-fb)/(a-b), d = fa - ca
    c = (fa - fb) / (a - b)
    d = fa - c * a
    
    question_text = f"請求出多項式 f(x) = {poly_to_string(f)} 除以 ({poly_to_string(g)}) 的餘式。"
    correct_answer = poly_to_string(np.poly1d([c, d]))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}