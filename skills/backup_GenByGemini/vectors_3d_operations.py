import random

def generate_vectors_3d_operations_question():
    """動態生成一道「空間向量的運算」的題目 (加減法)"""
    u_x, u_y, u_z = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    v_x, v_y, v_z = random.randint(-5, 5), random.randint(-5, 5), random.randint(-5, 5)
    op = random.choice(['+', '-'])
    
    if op == '+':
        res_x = u_x + v_x
        res_y = u_y + v_y
        res_z = u_z + v_z
    else: # op == '-'
        res_x = u_x - v_x
        res_y = u_y - v_y
        res_z = u_z - v_z
        
    component_choice = random.choice(['x', 'y', 'z'])
    
    if component_choice == 'x':
        question_text = f"已知向量 u = ({u_x}, {u_y}, {u_z}) 和向量 v = ({v_x}, {v_y}, {v_z})，請問向量 u {op} v 的 x 分量是多少？"
        answer = str(res_x)
    elif component_choice == 'y':
        question_text = f"已知向量 u = ({u_x}, {u_y}, {u_z}) 和向量 v = ({v_x}, {v_y}, {v_z})，請問向量 u {op} v 的 y 分量是多少？"
        answer = str(res_y)
    else: # 'z'
        question_text = f"已知向量 u = ({u_x}, {u_y}, {u_z}) 和向量 v = ({v_x}, {v_y}, {v_z})，請問向量 u {op} v 的 z 分量是多少？"
        answer = str(res_z)
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
