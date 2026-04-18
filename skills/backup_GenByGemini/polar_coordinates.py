import random

def generate_polar_coordinates_question():
    """動態生成一道「極坐標」的題目 (極座標轉直角座標)"""
    r = random.randint(2, 10)
    angle_deg = random.choice([0, 90, 180, 270])
    
    cos_val = 0
    sin_val = 0
    if angle_deg == 0:
        cos_val = 1
    elif angle_deg == 90:
        sin_val = 1
    elif angle_deg == 180:
        cos_val = -1
    elif angle_deg == 270:
        sin_val = -1

    x = r * cos_val
    y = r * sin_val

    if random.choice([True, False]):
         question_text = f"將極坐標點 [{r}, {angle_deg}°] 轉換為直角坐標 (x, y)，請問 x 坐標是多少？"
         answer = str(int(x))
    else:
         question_text = f"將極坐標點 [{r}, {angle_deg}°] 轉換為直角坐標 (x, y)，請問 y 坐標是多少？"
         answer = str(int(y))

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
