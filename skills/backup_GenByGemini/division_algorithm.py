# skills/division_algorithm.py
import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「多項式除法原理」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成商式 q(x) 和除式 g(x)
    q_coeffs = [random.randint(-3, 3) for _ in range(random.randint(2, 3))]
    g_coeffs = [random.randint(-2, 2) for _ in range(2)]
    while q_coeffs[0] == 0: q_coeffs[0] = random.randint(1, 3)
    while g_coeffs[0] == 0: g_coeffs[0] = random.randint(1, 2)
    q = np.poly1d(q_coeffs)
    g = np.poly1d(g_coeffs)

    # 隨機生成餘式 r(x)，次數需小於 g(x)
    r = np.poly1d(random.randint(-5, 5))

    # 計算被除式 f(x) = g(x) * q(x) + r(x)
    f = g * q + r

    f_str = poly_to_string(f)
    g_str = poly_to_string(g)
    r_str = poly_to_string(r)
    
    question_text = f"已知多項式 f(x) = {f_str}，若 f(x) 除以 {g_str} 的餘式為 {r_str}，請求出其商式 q(x)。"
    correct_answer = poly_to_string(q)
    context_string = f"根據除法原理 f(x)=g(x)q(x)+r(x)，從 f(x)={f_str}, g(x)={g_str}, r(x)={r_str} 求 q(x)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "handwritten", # 標記為手寫題，表示不需鍵盤輸入，答案供自行核對
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的商式是否正確。
    對於手寫題，此函數可能不會被調用進行自動檢查，或僅用於顯示正確答案供使用者自行核對。
    """
    user_clean = user_answer.replace(" ", "").replace("**", "^")
    correct_clean = correct_answer.replace(" ", "").replace("**", "^")
    if user_clean == correct_clean:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}