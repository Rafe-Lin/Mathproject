import random

def generate_circle_equation_question():
    center_x = random.randint(-3, 3)
    center_y = random.randint(-3, 3)
    radius = random.randint(2, 5)
    
    # Equation: (x - h)^2 + (y - k)^2 = r^2
    # Ask for the equation given center and radius
    question_text = f"已知圓心為 ({center_x}, {center_y})，半徑為 {radius}，求此圓的方程式。"
    
    # Answer format: (x-h)^2+(y-k)^2=r^2
    h_str = f"x - {abs(center_x)}" if center_x > 0 else f"x + {abs(center_x)}" if center_x < 0 else "x"
    k_str = f"y - {abs(center_y)}" if center_y > 0 else f"y + {abs(center_y)}" if center_y < 0 else "y"
    
    if center_x == 0 and center_y == 0:
        answer = f"x^2+y^2={radius**2}"
    elif center_x == 0:
        answer = f"x^2+({k_str})^2={radius**2}"
    elif center_y == 0:
        answer = f"({h_str})^2+y^2={radius**2}"
    else:
        answer = f"({h_str})^2+({k_str})^2={radius**2}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
