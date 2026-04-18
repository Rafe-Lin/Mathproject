# skills/slope_intercept_form.py
import random
import fractions

def format_slope_intercept(m, b):
    """將 y = mx + b 格式化為字串"""
    m_str = ""
    if m.denominator == 1:
        if m.numerator == 1: m_str = "x"
        elif m.numerator == -1: m_str = "-x"
        elif m.numerator != 0: m_str = f"{m.numerator}x"
    elif m.numerator != 0:
        if m.numerator < 0: m_str = f"- ({abs(m.numerator)}/{m.denominator})x"
        else: m_str = f"({m.numerator}/{m.denominator})x"

    b_str = ""
    if b > 0: b_str = f" + {b}"
    elif b < 0: b_str = f" - {abs(b)}"
    
    if not m_str and not b_str: return "y = 0"
    if not m_str: return f"y = {b}"
    
    return f"y = {m_str}{b_str}".replace("= x +", "= x + ").replace("= -x +", "= -x + ")

def generate(level=1):
    """
    生成一道「斜截式」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成斜率 m 和 y-截距 b
    m = fractions.Fraction(random.randint(-5, 5), random.randint(1, 3))
    b = random.randint(-7, 7)

    m_str = str(m.numerator) if m.denominator == 1 else f"{m.numerator}/{m.denominator}"

    question_text = (
        f"已知直線 L 的斜率為 {m_str}，y 截距為 {b}。\n"
        f"請寫出直線 L 的斜截式方程式 (y=mx+b)。"
    )
    
    correct_answer = format_slope_intercept(m, b)
    context_string = f"求斜率為 {m_str} 且 y 截距為 {b} 的直線方程式"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的方程式是否正確"""
    # 簡單比對，移除所有空格
    user_clean = user_answer.replace(" ", "")
    correct_clean = correct_answer.replace(" ", "")
    if user_clean == correct_clean:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}