import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「綜合除法」的題目。
    level 1: 除式為 x-k
    level 2: 除式為 x+k
    """
    f_deg = random.randint(3, 4)
    f_coeffs = [random.randint(-5, 5) for _ in range(f_deg + 1)]
    while f_coeffs[0] == 0: f_coeffs[0] = random.randint(1, 5)
    f = np.poly1d(f_coeffs)

    k = random.randint(1, 5) if level == 1 else random.randint(-5, -1)
    g = np.poly1d([1, -k])
    q, r = np.polydiv(f, g)

    question_text = f"請用綜合除法計算 ({poly_to_string(f)}) ÷ ({poly_to_string(g)}) 的商式與餘式。\n(格式：商式,餘式)"
    correct_answer = f"{poly_to_string(q)},{int(r[0]) if r.order==0 else poly_to_string(r)}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²").replace("^3","³")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}