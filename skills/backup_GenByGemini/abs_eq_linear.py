import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「一元一次絕對值方程式」的題目。
    |ax+b| = c
    """
    a = random.choice([-3, -2, 2, 3])
    b = random.randint(-10, 10)
    c = random.randint(1, 20)
    b_str = f"({b})" if b < 0 else str(b)

    question_text = f"請求解方程式：|{a}x + {b_str}| = {c} (若有兩解，請用逗號 , 分隔)"

    # ax+b = c  => x = (c-b)/a
    # ax+b = -c => x = (-c-b)/a
    sol1 = Fraction(c - b, a)
    sol2 = Fraction(-c - b, a)

    sol1_str = str(sol1.numerator) if sol1.denominator == 1 else f"{sol1.numerator}/{sol1.denominator}"
    sol2_str = str(sol2.numerator) if sol2.denominator == 1 else f"{sol2.numerator}/{sol2.denominator}"
    
    # 答案順序不重要，但為了標準化，我們排序
    correct_answers = sorted([sol1_str, sol2_str])
    correct_answer = ",".join(correct_answers)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_parts = sorted(correct_answer.strip().split(','))
    is_correct = (user_parts == correct_parts)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}