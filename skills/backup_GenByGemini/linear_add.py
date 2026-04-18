import random
from core.helpers import format_linear_equation_lhs, validate_linear_equation

def generate_addition_subtraction_question():
    """動態生成一道「加減消去法」的題目 (加入倍數變化)。"""
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)
    while x_sol == 0 or y_sol == 0:
        x_sol = random.randint(-5, 5)
        y_sol = random.randint(-5, 5)
    a1 = random.randint(-5, 5)
    b1 = random.randint(-5, 5)
    while a1 == 0 or b1 == 0:
        a1 = random.randint(-5, 5)
        b1 = random.randint(-5, 5)
    multiplier = random.choice([-3, -2, 2, 3])
    b2 = b1 * multiplier
    a2 = random.randint(-5, 5)
    while a2 == 0 or a2 == a1 * multiplier:
        a2 = random.randint(-5, 5)
    c1 = (a1 * x_sol) + (b1 * y_sol)
    c2 = (a2 * x_sol) + (b2 * y_sol)
    eq1_lhs = format_linear_equation_lhs(a1, b1)
    eq2_lhs = format_linear_equation_lhs(a2, b2)
    ask_for = random.choice(["x", "y"])
    answer = str(x_sol) if ask_for == "x" else str(y_sol)
    question_text = (f"請用加減消去法解下列聯立方程式：\n"
                    f"  {eq1_lhs:<15} = {c1:<10} ...... (1)\n"
                    f"  {eq2_lhs:<15} = {c2:<10} ...... (2)\n\n"
                    f"請問 {ask_for} = ?")
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": validate_linear_equation.__name__
    }
