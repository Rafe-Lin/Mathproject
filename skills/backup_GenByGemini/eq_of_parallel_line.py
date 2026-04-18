# skills/eq_of_parallel_line.py
import random

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
    生成一道「平行線方程式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成基準線 L: ax + by + c = 0
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    while a == 0 and b == 0:
        a, b = random.randint(-5, 5), random.randint(-5, 5)
    c = random.randint(-10, 10)
    
    # 隨機生成一個不在基準線上的點 P(x0, y0)
    x0, y0 = random.randint(-5, 5), random.randint(-5, 5)
    while a * x0 + b * y0 + c == 0:
        x0, y0 = random.randint(-5, 5), random.randint(-5, 5)

    # 平行線方程式為 ax + by + k = 0，將 P 點代入求 k
    k = -(a * x0 + b * y0)

    base_line_str = format_general_equation(a, b, c)
    correct_answer = format_general_equation(a, b, k)

    question_text = (
        f"已知直線 L₁ 與直線 L: {base_line_str} 平行，且 L₁ 通過點 P({x0}, {y0})。\n"
        f"請寫出直線 L₁ 的一般式方程式 (ax+by+c=0)。"
    )
    context_string = f"求過點 P({x0}, {y0}) 且與 {base_line_str} 平行的直線方程式"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的方程式是否正確"""
    user_clean = user_answer.replace(" ", "").replace("=0", "")
    correct_clean = correct_answer.replace(" ", "").replace("=0", "")
    if user_clean == correct_clean:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}