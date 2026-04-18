import random

def generate_coordinate_systems_question():
    """動態生成一道「坐標系」的題目 (直角坐標轉極坐標)"""
    # 選擇一個容易轉換的點，例如在軸上或特殊角度
    choice = random.choice([1, 2, 3, 4])
    if choice == 1: # (r, 0)
        x = random.randint(1, 5)
        y = 0
        r = x
        theta_deg = 0
    elif choice == 2: # (0, r)
        x = 0
        y = random.randint(1, 5)
        r = y
        theta_deg = 90
    elif choice == 3: # (-r, 0)
        x = random.randint(-5, -1)
        y = 0
        r = abs(x)
        theta_deg = 180
    else: # (0, -r)
        x = 0
        y = random.randint(-5, -1)
        r = abs(y)
        theta_deg = 270
        
    question_text = f"將直角坐標點 ({x}, {y}) 轉換為極坐標 (r, θ)，請問 r 的值是多少？"
    answer = str(r)
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
