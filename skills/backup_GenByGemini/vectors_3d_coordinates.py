import random

def generate_vectors_3d_coordinates_question():
    """動態生成一道「空間向量的坐標表示法」的題目 (向量分量)"""
    x1, y1, z1 = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    x2, y2, z2 = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    
    vec_x = x2 - x1
    vec_y = y2 - y1
    vec_z = z2 - z1
    
    component_choice = random.choice(['x', 'y', 'z'])
    
    if component_choice == 'x':
        question_text = f"已知空間中兩點 A({x1}, {y1}, {z1}) 和 B({x2}, {y2}, {z2})，請問向量 AB 的 x 分量是多少？"
        answer = str(vec_x)
    elif component_choice == 'y':
        question_text = f"已知空間中兩點 A({x1}, {y1}, {z1}) 和 B({x2}, {y2}, {z2})，請問向量 AB 的 y 分量是多少？"
        answer = str(vec_y)
    else: # 'z'
        question_text = f"已知空間中兩點 A({x1}, {y1}, {z1}) 和 B({x2}, {y2}, {z2})，請問向量 AB 的 z 分量是多少？"
        answer = str(vec_z)
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
