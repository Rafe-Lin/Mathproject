# skills/distance_point_line.py
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
    生成一道「點到直線距離公式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 從畢氏三元數中選擇 a, b，確保分母為整數
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
    a_base, b_base, den = random.choice(pythagorean_triples)
    a = random.choice([a_base, -a_base, b_base, -b_base])
    b = random.choice([b_base, -b_base])
    if abs(a) == abs(b): a = a_base # 避免 a, b 相同

    # 預設一個整數答案
    distance = random.randint(1, 5)
    numerator = distance * den
    
    # 隨機生成點 P(x0, y0) 和 c
    x0, y0 = random.randint(-5, 5), random.randint(-5, 5)
    c = random.randint(-10, 10)

    # 反向調整 c，使得 |ax0 + by0 + c| = numerator
    current_numerator = a * x0 + b * y0 + c
    # 我們需要 |current_numerator + delta_c| = numerator
    # 讓 current_numerator + delta_c = ±numerator
    delta_c = random.choice([numerator, -numerator]) - current_numerator
    c += delta_c

    correct_answer = str(distance)

    line_str = format_general_equation(a, b, c)
    question_text = f"請求出點 P({x0}, {y0}) 到直線 L: {line_str} 的距離。"
    context_string = f"計算點 P({x0}, {y0}) 到直線 L: {line_str} 的距離"

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