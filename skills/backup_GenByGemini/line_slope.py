import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「計算斜率」的題目。
    level 1: 兩點座標為整數，斜率為整數。
    level 2: 兩點座標為整數，斜率為分數。
    """
    if level == 1:
        # m = (y2-y1)/(x2-x1), m is integer
        m = random.randint(-5, 5)
        x1, y1 = random.randint(-10, 10), random.randint(-10, 10)
        x2 = x1 + random.randint(-3, 3)
        while x1 == x2: x2 = x1 + random.randint(-3, 3)
        y2 = y1 + m * (x2 - x1)
    else: # level 2
        # m is fraction
        m = Fraction(random.randint(-5, 5), random.randint(1, 5))
        x1, y1 = random.randint(-10, 10), random.randint(-10, 10)
        # x2-x1 is multiple of denominator
        x2 = x1 + m.denominator * random.randint(-2,2)
        while x1 == x2: x2 = x1 + m.denominator * random.randint(-2,2)
        y2 = y1 + m * (x2 - x1)

    question_text = f"請問通過 A({x1}, {y1}) 與 B({x2}, {y2}) 兩點的直線斜率是多少？"
    
    m_final = Fraction(y2 - y1, x2 - x1)
    if m_final.denominator == 1:
        correct_answer = str(m_final.numerator)
    else:
        correct_answer = f"{m_final.numerator}/{m_final.denominator}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}