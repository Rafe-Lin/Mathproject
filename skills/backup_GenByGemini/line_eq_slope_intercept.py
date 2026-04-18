import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「斜截式」求直線方程式的題目。
    level 1: 斜率和截距為整數。
    level 2: 斜率或截距為分數。
    """
    if level == 1:
        m = random.randint(-4, 4)
        c_intercept = random.randint(-5, 5)
        m_str = str(m)
    else: # level 2
        m = Fraction(random.randint(-5, 5), random.randint(2, 4))
        c_intercept = Fraction(random.randint(-5, 5), random.randint(2, 4))
        m_str = f"{m.numerator}/{m.denominator}"

    c_str = str(c_intercept) if isinstance(c_intercept, int) else f"{c_intercept.numerator}/{c_intercept.denominator}"
    question_text = f"已知直線 L 的斜率為 {m_str} 且 y 截距為 {c_str}，請求出直線 L 的方程式 (y=mx+c)。"

    # y = mx + c
    m_part = f"{m}x" if m != 1 else "x"
    m_part = f"-x" if m == -1 else m_part
    
    c_part = f"+{c_intercept}" if c_intercept > 0 else str(c_intercept)
    if c_intercept == 0: c_part = ""

    correct_answer = f"y={m_part}{c_part}".replace("+-", "-")

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}