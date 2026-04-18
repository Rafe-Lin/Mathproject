import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「因式定理」的題目。
    level 1: 判斷 x-k 是否為因式。
    level 2: 判斷 ax-b 是否為因式。
    """
    is_factor = random.choice([True, False])
    
    if level == 1:
        k = random.randint(-4, 4)
        g_str = f"x - {k}" if k >= 0 else f"x + {abs(k)}"
        root = k
    else: # level 2
        a, b = random.randint(2, 4), random.randint(-5, 5)
        g_str = f"{a}x - {b}" if b >= 0 else f"{a}x + {abs(b)}"
        root = b/a

    other_factor = np.poly1d([random.randint(1,3), random.randint(-3,3)])
    f = np.poly1d([1, -root]) * other_factor if is_factor else np.poly1d([random.randint(1,3), random.randint(-3,3), random.randint(-3,3)])
    
    question_text = f"請問 ({g_str}) 是否為多項式 f(x) = {poly_to_string(f)} 的因式？ (是/否)"
    correct_answer = "是" if np.isclose(f(root), 0) else "否"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}