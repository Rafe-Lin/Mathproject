import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「多項式長除法」的題目。
    level 1: 除式為一次式。
    level 2: 除式為二次式。
    """
    f_deg = random.randint(3, 4)
    f_coeffs = [random.randint(-5, 5) for _ in range(f_deg + 1)]
    while f_coeffs[0] == 0: f_coeffs[0] = random.randint(1, 5)
    
    if level == 1:
        g_deg = 1
    else: # level 2
        g_deg = 2
        
    g_coeffs = [random.randint(-3, 3) for _ in range(g_deg + 1)]
    while g_coeffs[0] == 0: g_coeffs[0] = random.randint(1, 3)

    f = np.poly1d(f_coeffs)
    g = np.poly1d(g_coeffs)
    
    q, r = np.polydiv(f, g)

    question_text = f"請計算 ({poly_to_string(f)}) ÷ ({poly_to_string(g)}) 的商式與餘式。\n(格式：商式,餘式)"
    correct_answer = f"{poly_to_string(q)},{poly_to_string(r)}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²").replace("^3","³")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}