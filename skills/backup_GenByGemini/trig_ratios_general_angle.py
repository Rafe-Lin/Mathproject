import random

def generate_trig_ratios_general_angle_question():
    """動態生成一道「廣義角三角比」的題目 (有理數答案)"""
    options = [
        (150, 'sin', '1/2'), (210, 'sin', '-1/2'), (330, 'sin', '-1/2'),
        (120, 'cos', '-1/2'), (240, 'cos', '-1/2'),
        (135, 'tan', '-1'), (225, 'tan', '1'), (315, 'tan', '-1')
    ]
    angle_deg, trig_func, answer = random.choice(options)
    question_text = f"請問 {trig_func}({angle_deg}°) 的值是多少？(請以數字或 a/b 的形式表示)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
