import random

def generate_vectors_2d_question():
    """動態生成一道「平面向量」的題目 (分量或長度)"""
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
    vec_x = x2 - x1
    vec_y = y2 - y1
    if random.choice([True, False]):
        question_text = f"已知點 A({x1}, {y1}) 和點 B({x2}, {y2})，請問向量 AB 的 x 分量是多少？"
        answer = str(vec_x)
    else:
        question_text = f"已知點 A({x1}, {y1}) 和點 B({x2}, {y2})，請問向量 AB 的 y 分量是多少？"
        answer = str(vec_y)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
