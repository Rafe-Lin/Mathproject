import random

def generate_ellipse_question():
    """動態生成一道「橢圓」的題目 (求中心點)"""
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)
    a_sq = random.randint(4, 9) # a^2
    b_sq = random.randint(1, 3) # b^2
    
    # (x-h)^2/a^2 + (y-k)^2/b^2 = 1
    # 為了簡化，我們只問中心點
    
    question_text = f"已知橢圓方程式為 (x - {h})^2/{a_sq} + (y - {k})^2/{b_sq} = 1，請問此橢圓的中心點坐標為何？ (請以 (x,y) 的格式回答，無須空格)"
    answer = f"({h},{k})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
