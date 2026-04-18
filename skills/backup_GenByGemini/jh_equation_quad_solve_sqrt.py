# skills/jh_equation_quad_solve_sqrt.py
import random

def generate(level=1):
    """
    生成一道「利用平方根解一元二次方程式」的題目。
    """
    # 構造 (ax+b)^2 = c 的形式
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    c_sqrt = random.randint(1, 7)
    c = c_sqrt**2

    equation_str = f"({a}x {'+' if b > 0 else '-'} {abs(b)})² = {c}"
    if b == 0: equation_str = f"({a}x)² = {c}"

    question_text = f"請利用平方根的概念解一元二次方程式：\n{equation_str}\n若有兩解，請用逗號分隔 (例如: 3,-5)"
    
    # 解為 ax+b = ±sqrt(c) => x = (-b ± sqrt(c))/a
    from fractions import Fraction
    sol1 = Fraction(-b + c_sqrt, a)
    sol2 = Fraction(-b - c_sqrt, a)
    
    sol1_str = str(sol1.numerator) if sol1.denominator == 1 else f"{sol1.numerator}/{sol1.denominator}"
    sol2_str = str(sol2.numerator) if sol2.denominator == 1 else f"{sol2.numerator}/{sol2.denominator}"
    correct_answer = f"{sol1_str},{sol2_str}"

    context_string = "利用 x² = k，則 x = ±√k 的原理來求解。"

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