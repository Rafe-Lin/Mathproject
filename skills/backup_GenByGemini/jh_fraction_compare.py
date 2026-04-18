# skills/jh_fraction_compare.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「分數比較大小」的題目。
    """
    den1 = random.randint(2, 10)
    num1 = random.randint(1, den1 - 1)
    f1 = Fraction(num1, den1)

    den2 = random.randint(2, 10)
    num2 = random.randint(1, den2 - 1)
    f2 = Fraction(num2, den2)

    while f1 == f2:
        den2 = random.randint(2, 10)
        num2 = random.randint(1, den2 - 1)
        f2 = Fraction(num2, den2)

    if f1 > f2:
        correct_answer = ">"
    else:
        correct_answer = "<"

    question_text = f"請比較 $\\frac{{{f1.numerator}}}{{{f1.denominator}}}$ 和 $\\frac{{{f2.numerator}}}{{{f2.denominator}}}$ 的大小。\n請在下方填入 > 或 <。"

    context_string = f"比較分數大小，可以通分或交叉相乘。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}