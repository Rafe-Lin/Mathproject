import random
import numpy as np
from fractions import Fraction

def generate(level=1):
    """
    生成一道「綜合除法 (除式為ax-b)」的題目。
    level 1: a, b 為整數，商式係數為整數。
    level 2: a, b 為整數，商式係數可能為分數。
    """
    f_deg = 3
    a = random.randint(2, 4)
    # 讓 f 的係數是 a 的倍數，這樣 level 1 的商式係數才會是整數
    f_coeffs = [random.randint(-3, 3) * a for _ in range(f_deg + 1)] if level == 1 else [random.randint(-5, 5) for _ in range(f_deg + 1)]
    while f_coeffs[0] == 0: f_coeffs[0] = random.randint(1, 3) * a
    f = np.poly1d(f_coeffs)

    b = random.randint(-5, 5)
    while b == 0: b = random.randint(-5, 5)
    g = np.poly1d([a, -b])
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