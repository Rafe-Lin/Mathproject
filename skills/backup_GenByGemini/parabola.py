import random
from math import gcd

def generate_parabola_question():
    """動態生成一道「拋物線」的題目 (求頂點)"""
    # 考慮兩種基本形式: y = a(x-h)^2 + k 或 x = a(y-k)^2 + h
    # 這裡我們生成 y = ax^2 + bx + c 形式，求頂點 (-b/2a, f(-b/2a))
    
    a = random.randint(-3, 3)
    while a == 0: # 確保是二次項
        a = random.randint(-3, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    # 頂點 x 座標: -b / (2a)
    vertex_x_num = -b
    vertex_x_den = 2 * a
    
    # 簡化分數
    common_divisor = gcd(vertex_x_num, vertex_x_den)
    vertex_x_num //= common_divisor
    vertex_x_den //= common_divisor
    
    question_text = f"已知拋物線方程式為 y = {a}x^2 + {b}x + {c}，請問其頂點的 x 坐標是多少？"
    
    if vertex_x_den == 1:
        answer = str(vertex_x_num)
    else:
        answer = f"{vertex_x_num}/{vertex_x_den}"
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
