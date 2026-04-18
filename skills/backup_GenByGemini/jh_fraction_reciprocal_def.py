# skills/jh_fraction_reciprocal_def.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「倒數定義」的題目。
    """
    # 隨機生成一個真分數、假分數或整數
    type = random.choice(['proper', 'improper', 'integer'])
    if type == 'proper':
        den = random.randint(2, 9)
        num = random.randint(1, den - 1)
    elif type == 'improper':
        den = random.randint(2, 9)
        num = random.randint(den + 1, 15)
    else: # integer
        num = random.randint(2, 9)
        den = 1

    f = Fraction(num, den)
    reciprocal = 1 / f

    f_str = str(f.numerator) if f.denominator == 1 else f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
    question_text = f"請問 ${f_str}$ 的倒數是多少？"
    correct_answer = f"{reciprocal.numerator}/{reciprocal.denominator}"

    context_string = f"一個不為0的數的倒數，是將該數的分子和分母對調。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    try:
        user_frac = Fraction(user_answer.strip())
        correct_frac = Fraction(correct_answer.strip())
        is_correct = user_frac == correct_frac
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    except (ValueError, ZeroDivisionError):
        is_correct = False
        result_text = f"請輸入分數格式，例如 3/4。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}