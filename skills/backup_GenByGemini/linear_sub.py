import random
from core.helpers import format_linear_equation_lhs, validate_linear_equation

def generate_substitution_question():
    """動態生成一道「帶入消去法」的題目 (確保唯一解)。"""
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)
    while x_sol == 0 or y_sol == 0:
        x_sol = random.randint(-5, 5)
        y_sol = random.randint(-5, 5)
    if random.choice([True, False]):  # 產生 y = mx + k
        m = random.randint(-3, 3)
        while m == 0:
            m = random.randint(-3, 3)
        k = y_sol - (m * x_sol)
        eq1_lhs = "y"
        eq1_rhs = f"{m}x"
        if k > 0:
            eq1_rhs += f" + {k}"
        elif k < 0:
            eq1_rhs += f" - {abs(k)}"
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        while a == 0 or b == 0 or a == -m * b:
            a = random.randint(-3, 3)
            b = random.randint(-3, 3)
        c = (a * x_sol) + (b * y_sol)
        eq2_lhs = format_linear_equation_lhs(a, b)
        eq2_rhs = str(c)
    else:  # 產生 x = my + k
        m = random.randint(-3, 3)
        while m == 0:
            m = random.randint(-3, 3)
        k = x_sol - (m * y_sol)
        eq1_lhs = "x"
        eq1_rhs = f"{m}y"
        if k > 0:
            eq1_rhs += f" + {k}"
        elif k < 0:
            eq1_rhs += f" - {abs(k)}"
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        while a == 0 or b == 0 or b == -m * a:
            a = random.randint(-3, 3)
            b = random.randint(-3, 3)
        c = (a * x_sol) + (b * y_sol)
        eq2_lhs = format_linear_equation_lhs(a, b)
        eq2_rhs = str(c)
    ask_for = random.choice(["x", "y"])
    answer = str(x_sol) if ask_for == "x" else str(y_sol)
    question_text = (f"請用帶入消去法解下列聯立方程式：\n"
                    f"  {eq1_lhs:<15} = {eq1_rhs:<10} ...... (1)\n"
                    f"  {eq2_lhs:<15} = {eq2_rhs:<10} ...... (2)\n\n"
                    f"請問 {ask_for} = ?")
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": validate_linear_equation.__name__
    }
