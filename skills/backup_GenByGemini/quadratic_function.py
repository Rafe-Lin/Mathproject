import random
from math import gcd

def generate_quadratic_function_question():
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)

    # Find vertex (-b/2a)
    vertex_x_num = -b
    vertex_x_den = 2 * a
    
    # Simplify fraction
    common_divisor = gcd(vertex_x_num, vertex_x_den)
    vertex_x_num //= common_divisor
    vertex_x_den //= common_divisor

    question_text = f"已知二次函數 f(x) = {a}x^2 + {b}x + {c}，求其頂點的 x 座標。"
    
    if vertex_x_den == 1:
        answer = str(vertex_x_num)
    else:
        answer = f"{vertex_x_num}/{vertex_x_den}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
