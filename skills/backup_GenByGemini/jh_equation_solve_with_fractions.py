# skills/jh_equation_solve_with_fractions.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「解含分數的一元一次方程式」的題目。
    """
    # 為了讓解是整數，反向構造
    x = random.randint(-5, 5)
    den1 = random.randint(2, 5)
    den2 = random.randint(2, 5)
    
    # (x/den1) + a = b
    a_num = random.randint(1, 5)
    a_den = random.randint(2, 5)
    a = Fraction(a_num, a_den)
    
    b = Fraction(x, den1) + a

    a_str = f"{a.numerator}/{a.denominator}"
    b_str = f"{b.numerator}/{b.denominator}"

    question_text = f"請求解方程式：$\\dfrac{{x}}{{{den1}}} + \\dfrac{{{a.numerator}}}{{{a.denominator}}} = \\dfrac{{{b.numerator}}}{{{b.denominator}}}$"

    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": f"解含分數的一元一次方程式"
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace("x=", "")
    correct = correct_answer.strip()
    try:
        if float(user) == float(correct):
            is_correct = True
            result_text = f"完全正確！答案是 x = {correct}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：x = {correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：x = {correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}