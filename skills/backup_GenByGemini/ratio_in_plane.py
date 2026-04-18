import random

def generate_ratio_in_plane_question():
    """動態生成一道「平面上的比例」的題目 (分點公式)"""
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
    
    m = random.randint(1, 3)
    n = random.randint(1, 3)
    
    # 內部一點 P 將 AB 線段分成 m:n
    # Px = (n*x1 + m*x2) / (m+n)
    # Py = (n*y1 + m*y2) / (m+n)
    
    px_num = n * x1 + m * x2
    py_num = n * y1 + m * y2
    den = m + n
    
    # 確保答案是整數，或者至少是簡單分數
    if px_num % den != 0 or py_num % den != 0:
        # 重新生成，直到得到整數解
        return generate_ratio_in_plane_question()
        
    px = px_num // den
    py = py_num // den
    
    question_text = (
        f"已知平面上兩點 A({x1}, {y1}) 和 B({x2}, {y2})。"
        f"若點 P 在線段 AB 上，且 AP:PB = {m}:{n}，請問點 P 的坐標為何？ (請以 (x,y) 的格式回答，無須空格)"
    )
    answer = f"({px},{py})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
