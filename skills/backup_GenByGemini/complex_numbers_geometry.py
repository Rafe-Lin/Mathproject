import random
import math

def generate_complex_numbers_geometry_question():
    """動態生成一道「複數的幾何意涵」的題目 (求模數)"""
    real_part = random.randint(-5, 5)
    imag_part = random.randint(-5, 5)
    
    # 確保不是 0+0i
    while real_part == 0 and imag_part == 0:
        real_part = random.randint(-5, 5)
        imag_part = random.randint(-5, 5)
        
    modulus = math.sqrt(real_part**2 + imag_part**2)
    
    complex_num_str = f"{real_part}{'+' if imag_part >= 0 else ''}{imag_part}i"
    
    question_text = f"請問複數 {complex_num_str} 的模數 (絕對值) 是多少？ (請四捨五入到小數點後一位)"
    answer = f"{modulus:.1f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
