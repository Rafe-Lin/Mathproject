# skills/jh_fraction_add_sub_same_den.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「同分母分數加減」的題目。
    """
    den = random.randint(3, 15)
    num1 = random.randint(1, den - 1)
    num2 = random.randint(1, den - 1)

    op = random.choice(['+', '-'])

    if op == '+':
        result_num = num1 + num2
    else:
        # 確保結果為正
        if num1 < num2:
            num1, num2 = num2, num1
        result_num = num1 - num2

    result = Fraction(result_num, den) # 自動約分

    question_text = f"請計算：$\\frac{{{num1}}}{{{den}}} {op} \\frac{{{num2}}}{{{den}}}$"
    correct_answer = f"{result.numerator}/{result.denominator}" if result.denominator != 1 else str(result.numerator)

    context_string = f"計算同分母分數加減，分母不變，分子相加減。"

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