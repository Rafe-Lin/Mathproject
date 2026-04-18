# skills/jh_equation_quad_solve_formula.py
import random
import math

def generate(level=1):
    """
    生成一道「公式解解一元二次方程式」的題目。
    """
    # 構造 b^2-4ac 為完全平方數，使解為有理數
    while True:
        a = random.randint(1, 3)
        b = random.randint(-7, 7)
        c = random.randint(-7, 7)
        discriminant = b**2 - 4*a*c
        if discriminant >= 0 and math.isqrt(discriminant)**2 == discriminant:
            break

    equation_str = f"{a}x² {'+' if b > 0 else '-'} {abs(b)}x {'+' if c > 0 else '-'} {abs(c)} = 0"

    question_text = f"請用「公式解」解一元二次方程式：\n{equation_str}\n若有兩解，請用逗號分隔 (例如: 3/2,-5)"
    
    # 計算解
    from fractions import Fraction
    sqrt_d = math.isqrt(discriminant)
    sol1 = Fraction(-b + sqrt_d, 2*a)
    sol2 = Fraction(-b - sqrt_d, 2*a)
    
    sol1_str = str(sol1.numerator) if sol1.denominator == 1 else f"{sol1.numerator}/{sol1.denominator}"
    sol2_str = str(sol2.numerator) if sol2.denominator == 1 else f"{sol2.numerator}/{sol2.denominator}"
    correct_answer = f"{sol1_str},{sol2_str}"

    context_string = "利用一元二次方程式公式解 x = (-b ± sqrt(b²-4ac)) / 2a 來求解。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user_sols = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_sols = sorted(correct_answer.strip().split(','))
    is_correct = user_sols == correct_sols
    result_text = f"完全正確！解為 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}