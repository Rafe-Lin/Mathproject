import random

def generate_data_analysis_2d_question():
    """動態生成一道「二維數據分析」的題目 (求中心點)"""
    data_points = []
    x_sum = 0
    y_sum = 0
    n = 5
    for _ in range(n):
        x = random.randint(1, 10)
        y = random.randint(1, 10)
        data_points.append(f"({x}, {y})")
        x_sum += x
        y_sum += y
    mean_x = x_sum / n
    mean_y = y_sum / n
    mean_x_str = f"{mean_x:.1f}" if mean_x != int(mean_x) else str(int(mean_x))
    mean_y_str = f"{mean_y:.1f}" if mean_y != int(mean_y) else str(int(mean_y))
    points_str = ", ".join(data_points)
    question_text = f"給定 {n} 組二維數據 (X, Y): {points_str}，請問此數據的中心點 (X的平均數, Y的平均數) 是什麼？(請以 (x,y) 的格式回答，無須空格)"
    answer = f"({mean_x_str},{mean_y_str})"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
