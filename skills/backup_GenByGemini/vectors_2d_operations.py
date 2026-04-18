import random

def generate_vectors_2d_operations_question():
    """動態生成一道「平面向量的運算」的題目 (加減法)"""
    ux, uy = random.randint(-5, 5), random.randint(-5, 5)
    vx, vy = random.randint(-5, 5), random.randint(-5, 5)
    op = random.choice(['+', '-'])
    if op == '+':
        res_x = ux + vx
        res_y = uy + vy
    else:
        res_x = ux - vx
        res_y = uy - vy
    if random.choice([True, False]):
        question_text = f"已知向量 u = ({ux}, {uy}) 和向量 v = ({vx}, {vy})，請問向量 u {op} v 的 x 分量是多少？"
        answer = str(res_x)
    else:
        question_text = f"已知向量 u = ({ux}, {uy}) 和向量 v = ({vx}, {vy})，請問向量 u {op} v 的 y 分量是多少？"
        answer = str(res_y)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
