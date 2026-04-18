import random

def generate_circle_line_question():
    # Simple question: determine if a point is on a circle
    center_x = random.randint(-3, 3)
    center_y = random.randint(-3, 3)
    radius = random.randint(2, 4)
    
    # Generate a point (px, py)
    px = random.randint(center_x - radius - 1, center_x + radius + 1)
    py = random.randint(center_y - radius - 1, center_y + radius + 1)
    
    # Check if the point is on the circle
    distance_sq = (px - center_x)**2 + (py - center_y)**2
    is_on_circle = (distance_sq == radius**2)
    
    question_text = f"已知圓方程式為 (x - {center_x})^2 + (y - {center_y})^2 = {radius**2}，請問點 ({px}, {py}) 是否在此圓上？ (請回答 '是' 或 '否')"
    correct_answer = "是" if is_on_circle else "否"

    return {
        "text": question_text,
        "answer": correct_answer,
        "validation_function_name": None # Simple string comparison
    }
