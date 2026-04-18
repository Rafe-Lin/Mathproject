import random

def generate_lines_in_space_question():
    """動態生成一道「空間中的直線」的題目 (求方向向量)"""
    # 點 (x0, y0, z0) 和方向向量 (a, b, c)
    x0, y0, z0 = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    a, b, c = random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)
    
    # 確保方向向量不是零向量
    while a == 0 and b == 0 and c == 0:
        a, b, c = random.randint(-3, 3), random.randint(-3, 3), random.randint(-3, 3)
        
    # 參數式: x = x0 + at, y = y0 + bt, z = z0 + ct
    question_text = f"已知空間中一條直線的參數式為 x = {x0}{'+' if a >= 0 else ''}{a}t, y = {y0}{'+' if b >= 0 else ''}{b}t, z = {z0}{'+' if c >= 0 else ''}{c}t，請問此直線的一個方向向量為何？ (請以 (a,b,c) 的格式回答，無須空格)"
    answer = f"({a},{b},{c})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
