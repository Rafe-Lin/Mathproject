# skills/jh_fraction_add_sub_diff_den.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「異分母分數加減」的題目。
    """
    den1 = random.randint(2, 7)
    num1 = random.randint(1, den1 - 1)
    f1 = Fraction(num1, den1)

    den2 = random.randint(2, 7)
    while den1 == den2:
        den2 = random.randint(2, 7)
    num2 = random.randint(1, den2 - 1)
    f2 = Fraction(num2, den2)

    op = random.choice(['+', '-'])

    if op == '+':
        result = f1 + f2
    else:
        result = f1 - f2

    question_text = f"請計算：$\\frac{{{f1.numerator}}}{{{f1.denominator}}} {op} \\frac{{{f2.numerator}}}{{{f2.denominator}}}$"
    correct_answer = f"{result.numerator}/{result.denominator}"

    context_string = f"計算異分母分數加減，需要先通分。"

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
    try:
        user_frac = Fraction(user_answer.strip())
        correct_frac = Fraction(correct_answer.strip())
        is_correct = user_frac == correct_frac
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    except (ValueError, ZeroDivisionError):
        is_correct = False
        result_text = f"請輸入分數格式，例如 3/4。正確答案是：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": is_correct}