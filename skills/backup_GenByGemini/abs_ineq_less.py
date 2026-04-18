import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「絕對值不等式 (小於)」的題目。
    |ax+b| < c  => -c < ax+b < c
    """
    c = random.randint(1, 10)
    a = random.choice([-3, -2, 2, 3])
    b = random.randint(-10, 10)
    b_str = f"({b})" if b < 0 else str(b)

    op = random.choice(['<', '<='])
    question_text = f"請求解不等式：|{a}x + {b_str}| {op} {c}"

    # -c < ax+b < c  => -c-b < ax < c-b
    lower = Fraction(-c - b, a)
    upper = Fraction(c - b, a)

    if a < 0: # a為負，不等式反向
        lower, upper = upper, lower

    lower_str = str(lower.numerator) if lower.denominator == 1 else f"{lower.numerator}/{lower.denominator}"
    upper_str = str(upper.numerator) if upper.denominator == 1 else f"{upper.numerator}/{upper.denominator}"

    correct_answer = f"{lower_str} {op} x {op} {upper_str}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    # 簡單比對，移除空白
    user = user_answer.replace(" ", "")
    correct = correct_answer.replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}