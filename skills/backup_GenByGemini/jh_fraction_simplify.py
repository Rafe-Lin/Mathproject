# skills/jh_fraction_simplify.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「分數約分」的題目。
    """
    # 先決定最簡分數
    den_simple = random.randint(2, 7)
    num_simple = random.randint(1, den_simple - 1)
    
    # 再乘以一個公因數來擴分
    common_factor = random.randint(2, 5)
    
    num_orig = num_simple * common_factor
    den_orig = den_simple * common_factor

    question_text = f"請將分數 $\\frac{{{num_orig}}}{{{den_orig}}}$ 化為最簡分數。"
    correct_answer = f"{num_simple}/{den_simple}"

    context_string = f"將分數化為最簡分數，即分子分母同除以其最大公因數。"

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
        # 將使用者答案和正確答案都轉為 Fraction 物件來比較
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