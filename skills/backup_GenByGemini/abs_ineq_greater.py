import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「絕對值不等式 (大於)」的題目。
    |ax+b| > c  => ax+b > c 或 ax+b < -c
    """
    c = random.randint(1, 10)
    a = random.choice([-3, -2, 2, 3])
    b = random.randint(-10, 10)
    b_str = f"({b})" if b < 0 else str(b)

    op = random.choice(['>', '>='])
    question_text = f"請求解不等式：|{a}x + {b_str}| {op} {c}"

    # ax+b > c  => ax > c-b
    # ax+b < -c => ax < -c-b
    bound1 = Fraction(c - b, a)
    bound2 = Fraction(-c - b, a)

    if a > 0:
        correct_answer = f"x {op} {max(bound1, bound2)} 或 x {'<=' if op == '>=' else '<'} {min(bound1, bound2)}"
    else: # a < 0, 不等式反向
        correct_answer = f"x {'<=' if op == '>=' else '<'} {min(bound1, bound2)} 或 x {op} {max(bound1, bound2)}"

    # 將分數格式化
    correct_answer = correct_answer.replace("Fraction", "")

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    # 簡單比對，移除空白，並考慮 "或" 的兩邊順序
    user_parts = sorted([p.strip() for p in user_answer.replace(" ", "").split('或')])
    correct_parts = sorted([p.strip() for p in correct_answer.replace(" ", "").split('或')])
    is_correct = (user_parts == correct_parts)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}