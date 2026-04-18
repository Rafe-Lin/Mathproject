import random

def generate_hyperbola_question():
    """動態生成一道「雙曲線」的題目 (求中心點)"""
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)
    a_sq = random.randint(4, 9) # a^2
    b_sq = random.randint(1, 3) # b^2
    
    # (x-h)^2/a^2 - (y-k)^2/b^2 = 1 或 (y-k)^2/b^2 - (x-h)^2/a^2 = 1
    # 為了簡化，我們只問中心點
    
    if random.choice([True, False]):
        equation_str = f"(x - {h})^2/{a_sq} - (y - {k})^2/{b_sq} = 1"
    else:
        equation_str = f"(y - {k})^2/{b_sq} - (x - {h})^2/{a_sq} = 1"
        
    question_text = f"已知雙曲線方程式為 {equation_str}，請問此雙曲線的中心點坐標為何？ (請以 (x,y) 的格式回答，無須空格)"
    answer = f"({h},{k})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
