# skills/remainder_theorem.py
import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「餘式定理」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 生成一個 2 或 3 次多項式
    coeffs = [random.randint(-5, 5) for _ in range(random.randint(3, 4))]
    while coeffs[0] == 0: coeffs[0] = random.randint(1, 5)
    f = np.poly1d(coeffs)

    # 除式 ax - b
    # 為了確保餘數為整數，我們只使用 x-k 的形式
    k = random.randint(-4, 4)
    while k == 0: k = random.randint(-4, 4)
    
    divisor_str = f"x - {k}" if k > 0 else f"x + {abs(k)}"

    # 根據餘式定理，餘數為 f(k)
    remainder = f(k)
    correct_answer = str(int(remainder))

    question_text = f"請求出多項式 f(x) = {poly_to_string(f)} 除以 {divisor_str} 的餘式。"
    context_string = f"使用餘式定理計算 f(x) = {poly_to_string(f)} 除以 {divisor_str} 的餘式"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的餘式是否正確"""
    try:
        if abs(float(user_answer) - float(correct_answer)) < 1e-9:
            return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    except (ValueError, TypeError):
        pass
    is_correct = False
    result_text = f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}