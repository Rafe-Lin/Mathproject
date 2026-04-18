# skills/jh_ratio_def_value.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「比與比值」的題目。
    """
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    
    # 隨機問比值或給比值問比
    if random.choice([True, False]):
        # 問比值
        question_text = f"請問 {a} : {b} 的比值是多少？ (請以最簡分數表示)"
        frac = Fraction(a, b)
        correct_answer = f"{frac.numerator}/{frac.denominator}"
        if frac.denominator == 1:
            correct_answer = str(frac.numerator)
    else:
        # 給比值問比
        frac = Fraction(a, b)
        val_str = f"{frac.numerator}/{frac.denominator}" if frac.denominator != 1 else str(frac.numerator)
        question_text = f"如果 x 和 y 的比值為 {val_str}，請問 x : y 等於多少？ (請以最簡整數比表示)"
        correct_answer = f"{frac.numerator}:{frac.denominator}"

    context_string = "學習「比」的表示法 a:b，以及「比值」的計算 a/b。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    try:
        # 處理分數與整數的比較
        is_correct = Fraction(user) == Fraction(correct)
    except (ValueError, ZeroDivisionError):
        is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}