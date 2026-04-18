# skills/cross_multiplication.py
import random
import re
from .utils import poly_to_string

def format_factor(p, q):
    """將 (px + q) 格式化為字串"""
    if p == 1:
        p_str = "x"
    elif p == -1:
        p_str = "-x"
    else:
        p_str = f"{p}x"
    
    if q == 0:
        return f"({p_str})"
    
    sign = "+" if q > 0 else "-"
    abs_q = abs(q)
    return f"({p_str} {sign} {abs_q})"

def generate(level=1):
    """
    生成一道「十字交乘法」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 從因式分解 (px+q)(rx+s) 開始反向生成題目，確保係數為整數
    p = random.randint(1, 3)
    r = random.randint(1, 3)
    q = random.randint(-7, 7)
    s = random.randint(-7, 7)

    # 避免 q 或 s 為 0，這樣比較有十字交乘的意義
    while q == 0 or s == 0:
        q = random.randint(-7, 7)
        s = random.randint(-7, 7)

    # 展開 (px+q)(rx+s) = prx² + (ps+qr)x + qs
    a = p * r
    b = p * s + q * r
    c = q * s

    poly_str = poly_to_string([a, b, c])
    
    question_text = f"請使用十字交乘法，將二次多項式 {poly_str} 分解為兩個一次因式的乘積。"
    
    # 產生標準答案
    factor1 = format_factor(p, q)
    factor2 = format_factor(r, s)
    correct_answer = f"{factor1}{factor2}"
    
    context_string = f"將 {poly_str} 因式分解"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的因式分解是否正確。
    考慮到 (ax+b)(cx+d) 和 (cx+d)(ax+b) 是相同的。
    也考慮到 (-ax-b)(-cx-d) 是相同的。
    """
    # 清理輸入，移除所有空格
    user_clean = user_answer.replace(" ", "")
    correct_clean = correct_answer.replace(" ", "")

    # 直接比對
    if user_clean == correct_clean:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}

    # 嘗試交換順序後比對
    factors = re.findall(r'\(.*?\)', correct_clean)
    if len(factors) == 2:
        reversed_correct = f"{factors[1]}{factors[0]}"
        if user_clean == reversed_correct:
            return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}

    return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}