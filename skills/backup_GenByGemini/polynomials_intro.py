import random
from core.helpers import format_polynomial

def generate_polynomials_intro_question():
    """動態生成一道「多項式」的題目 (求次數)"""
    degree = random.randint(1, 4)
    coeffs = [random.randint(-5, 5) for _ in range(degree + 1)]
    
    # 確保最高次項係數不為零
    while coeffs[0] == 0:
        coeffs[0] = random.randint(-5, 5)
        
    poly_text = format_polynomial(coeffs)
    
    question_text = f"請問多項式 f(x) = {poly_text} 的次數是多少？"
    answer = str(degree)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
