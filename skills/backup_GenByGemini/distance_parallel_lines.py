# skills/distance_parallel_lines.py
import random
import math

def format_general_equation(a, b, c):
    """將 ax + by + c = 0 格式化為字串"""
    terms = []
    if a != 0:
        if a == 1: terms.append("x")
        elif a == -1: terms.append("-x")
        else: terms.append(f"{a}x")
    if b != 0:
        sign = " + " if b > 0 else " - "
        abs_b = abs(b)
        if abs_b == 1: terms.append(f"{sign}y")
        else: terms.append(f"{sign}{abs_b}y")
    if c != 0:
        sign = " + " if c > 0 else " - "
        terms.append(f"{sign}{abs(c)}")
    return "".join(terms).lstrip(" +") + " = 0"

def generate(level=1):
    """
    生成一道「兩平行線距離公式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 從畢氏三元數中選擇 a, b，確保分母為整數
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
    a_base, b_base, den = random.choice(pythagorean_triples)
    a = random.choice([a_base, -a_base, b_base, -b_base])
    b = random.choice([b_base, -b_base])
    if abs(a) == abs(b): a = a_base

    # 預設一個整數答案
    distance = random.randint(1, 5)
    c_diff = distance * den

    # 隨機生成 c1，然後計算 c2
    c1 = random.randint(-10, 10)
    c2 = c1 + random.choice([c_diff, -c_diff])

    correct_answer = str(distance)

    line1_str = format_general_equation(a, b, c1)
    line2_str = format_general_equation(a, b, c2)
    question_text = f"請求出兩平行線 L₁: {line1_str} 與 L₂: {line2_str} 之間的距離。"
    context_string = f"計算兩平行線 {line1_str} 與 {line2_str} 的距離"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的距離是否正確"""
    try:
        user_val = float(user_answer.strip())
        correct_val = float(correct_answer)
        if math.isclose(user_val, correct_val):
            return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    except ValueError:
        pass
    return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}