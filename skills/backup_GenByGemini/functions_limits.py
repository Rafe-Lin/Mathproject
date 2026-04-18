import random

def generate_functions_limits_question():
    """動態生成一道「函數與函數的極限」的題目 (求多項式函數的極限)"""
    # 簡單的多項式函數，直接代入即可
    a = random.randint(-3, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    x_val = random.randint(-2, 2)
    
    # f(x) = ax^2 + bx + c
    limit_val = a * (x_val**2) + b * x_val + c
    
    question_text = f"請問函數 f(x) = {a}x^2 + {b}x + {c} 在 x 趨近於 {x_val} 時的極限值是多少？"
    answer = str(limit_val)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
