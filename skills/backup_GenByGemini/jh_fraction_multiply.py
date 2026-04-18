# skills/jh_fraction_multiply.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「分數乘法」的題目。
    """
    den1 = random.randint(2, 9)
    num1 = random.randint(1, 9)
    f1 = Fraction(num1, den1)

    den2 = random.randint(2, 9)
    num2 = random.randint(1, 9)
    f2 = Fraction(num2, den2)

    result = f1 * f2

    question_text = f"請計算：$\\frac{{{f1.numerator}}}{{{f1.denominator}}} \\times \\frac{{{f2.numerator}}}{{{f2.denominator}}}$"
    correct_answer = f"{result.numerator}/{result.denominator}" if result.denominator != 1 else str(result.numerator)

    context_string = f"計算分數乘法，分子乘分子，分母乘分母，最後約分。"

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
        # 將使用者答案和正確答案都轉為 Fraction 物件來比較，可以忽略是否約分
        user_frac = Fraction(user_answer.strip())
        correct_frac = Fraction(correct_answer.strip())
        
        if user_frac == correct_frac:
            is_correct = True
            result_text = f"完全正確！答案是 {correct_answer}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：{correct_answer}"
    except (ValueError, ZeroDivisionError):
        is_correct = False
        result_text = f"請輸入分數格式，例如 3/4。正確答案是：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": is_correct}