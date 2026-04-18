import random

def generate_complex_plane_question():
    """動態生成一道「複數與複數平面」的題目 (從坐標判斷複數)"""
    real_part = random.randint(-5, 5)
    imag_part = random.randint(-5, 5)
    
    complex_num_str = f"{real_part}{'+' if imag_part >= 0 else ''}{imag_part}i"
    
    question_text = f"在複數平面上，點 ({real_part}, {imag_part}) 代表哪一個複數？ (請以 a+bi 的形式回答)"
    answer = complex_num_str
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
