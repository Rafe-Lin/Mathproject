import random

def generate_planes_in_space_question():
    """動態生成一道「空間中的平面」的題目 (求法向量)"""
    a, b, c = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    d = random.randint(-10, 10)
    
    # Ensure at least one coefficient is non-zero
    while a == 0 and b == 0 and c == 0:
        a, b, c = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
        
    equation_parts = []
    if a != 0:
        equation_parts.append(f"{a}x")
    if b != 0:
        if b > 0 and equation_parts:
            equation_parts.append(f" + {b}y")
        elif b < 0 and equation_parts:
            equation_parts.append(f" - {abs(b)}y")
        else:
            equation_parts.append(f"{b}y")
    if c != 0:
        if c > 0 and equation_parts:
            equation_parts.append(f" + {c}z")
        elif c < 0 and equation_parts:
            equation_parts.append(f" - {abs(c)}z")
        else:
            equation_parts.append(f"{c}z")
            
    equation_str = "".join(equation_parts)
    if not equation_str: # Should not happen if a,b,c are not all zero
        equation_str = "0"
        
    question_text = f"已知平面方程式為 {equation_str} = {d}，請問此平面的法向量為何？ (請以 (a,b,c) 的格式回答，無須空格)"
    answer = f"({a},{b},{c})"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
