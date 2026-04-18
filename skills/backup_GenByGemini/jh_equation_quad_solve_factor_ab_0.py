# skills/jh_equation_quad_solve_factor_ab_0.py
import random

def generate(level=1):
    """
    生成一道「因式分解法解一元二次方程式」的題目。
    """
    # 構造 (ax-b)(cx-d) = 0
    a = random.choice([1, 2])
    c = random.choice([1, 2, 3])
    b = random.randint(1, 5)
    d = random.randint(1, 5)
    
    # 為了讓題目看起來不是直接分解好的，把它展開
    # acx^2 - (ad+bc)x + bd = 0
    coeff_a = a * c
    coeff_b = -(a * d + b * c)
    coeff_c = b * d

    equation_str = f"{coeff_a}x² {'+' if coeff_b > 0 else '-'} {abs(coeff_b)}x + {coeff_c} = 0"

    question_text = f"請用「因式分解法」解一元二次方程式：\n{equation_str}\n若有兩解，請用逗號分隔 (例如: 3/2,5)"
    
    # 解為 x = b/a 或 x = d/c
    from fractions import Fraction
    sol1 = Fraction(b, a)
    sol2 = Fraction(d, c)
    
    sol1_str = str(sol1.numerator) if sol1.denominator == 1 else f"{sol1.numerator}/{sol1.denominator}"
    sol2_str = str(sol2.numerator) if sol2.denominator == 1 else f"{sol2.numerator}/{sol2.denominator}"
    correct_answer = f"{sol1_str},{sol2_str}"

    context_string = "利用 AB=0，則 A=0 或 B=0 的原理來求解。"

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