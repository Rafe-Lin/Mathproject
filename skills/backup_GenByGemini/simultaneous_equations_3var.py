import random

def generate_simultaneous_equations_3var_question():
    """動態生成一道「三元一次聯立方程式」的題目 (簡化版)"""
    # 確保有整數解，且題目不會太複雜
    x_sol = random.randint(-3, 3)
    y_sol = random.randint(-3, 3)
    z_sol = random.randint(-3, 3)
    
    # 方程式 1: 簡單的 x + y + z = C1
    c1 = x_sol + y_sol + z_sol
    eq1_str = f"x + y + z = {c1}"
    
    # 方程式 2: 2x + y - z = C2
    c2 = 2 * x_sol + y_sol - z_sol
    eq2_str = f"2x + y - z = {c2}"
    
    # 方程式 3: x - 2y + 3z = C3
    c3 = x_sol - 2 * y_sol + 3 * z_sol
    eq3_str = f"x - 2y + 3z = {c3}"
    
    ask_for = random.choice(['x', 'y', 'z'])
    if ask_for == 'x':
        answer = str(x_sol)
    elif ask_for == 'y':
        answer = str(y_sol)
    else:
        answer = str(z_sol)
        
    question_text = (
        f"請解下列聯立方程式：\n"
        f"  {eq1_str} ...... (1)\n"
        f"  {eq2_str} ...... (2)\n"
        f"  {eq3_str} ...... (3)\n\n"
        f"請問 {ask_for} = ?"
    )
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }

