# skills/slope_general_form.py
import random
import fractions

def format_general_equation(a, b, c):
    """將 ax + by + c = 0 格式化為字串"""
    terms = []
    # x term
    if a != 0:
        if a == 1: terms.append("x")
        elif a == -1: terms.append("-x")
        else: terms.append(f"{a}x")
    # y term
    if b != 0:
        sign = " + " if b > 0 else " - "
        abs_b = abs(b)
        if abs_b == 1: terms.append(f"{sign}y")
        else: terms.append(f"{sign}{abs_b}y")
    # constant term
    if c != 0:
        sign = " + " if c > 0 else " - "
        terms.append(f"{sign}{abs(c)}")
    
    return "".join(terms).lstrip(" +") + " = 0"

def generate(level=1):
    """
    生成一道「一般式求斜率」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成係數 a, b, c
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    # 確保 a, b 不全為 0，且 b 不為 0 (因為要求斜率)
    while b == 0 or (a == 0 and b == 0):
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
    c = random.randint(-10, 10)

    # 格式化方程式
    equation_str = format_general_equation(a, b, c)

    # 計算斜率 m = -a/b
    slope = fractions.Fraction(-a, b)

    # 格式化正確答案
    if slope.denominator == 1:
        correct_answer = str(slope.numerator)
    else:
        correct_answer = f"{slope.numerator}/{slope.denominator}"

    question_text = f"請問直線 L: {equation_str} 的斜率是多少？"
    context_string = f"從 {equation_str} 求斜率 m = -a/b"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的斜率是否正確"""
    user = user_answer.strip()
    correct = correct_answer.strip()
    try:
        if "/" in correct:
            num, den = map(int, correct.split('/'))
            correct_val = num / den
        else:
            correct_val = float(correct)

        if "/" in user:
            num, den = map(int, user.split('/'))
            user_val = num / den
        else:
            user_val = float(user)

        if abs(user_val - correct_val) < 1e-9:
            return {"correct": True, "result": f"完全正確！斜率是 {correct}。"}
        else:
            return {"correct": False, "result": f"答案不正確。正確答案是：{correct}"}
    except (ValueError, ZeroDivisionError):
        return {"correct": False, "result": f"請輸入有效的數字或分數格式。正確答案是：{correct}"}