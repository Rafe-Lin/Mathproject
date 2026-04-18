import random

def generate_complex_roots_polynomials_question():
    """動態生成一道「複數與多項式方程式的根」的題目 (共軛複數根)"""
    # 根據共軛複數根定理，如果一個實係數多項式有一個複數根 a+bi，那麼它的共軛複數 a-bi 也是一個根。
    
    # 生成一個複數根
    a = random.randint(-3, 3)
    b = random.randint(1, 3) # 確保 b 不為 0，是純虛數部分
    
    complex_root_str = f"{a}{'+' if b > 0 else ''}{b}i"
    conjugate_root_str = f"{a}{'-' if b > 0 else '+'}{abs(b)}i"
    
    question_text = (
        f"已知一個實係數多項式方程式有一個根為 {complex_root_str}。"
        f"請問此多項式方程式的另一個根為何？"
    )
    answer = conjugate_root_str
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
