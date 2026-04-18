import random

def generate_radian_measure_question():
    """動態生成一道「弧度量」的題目 (角度與弧度互換)"""
    deg_to_rad = {
        30: "pi/6", 60: "pi/3", 90: "pi/2", 120: "2*pi/3",
        180: "pi", 270: "3*pi/2", 360: "2*pi"
    }
    deg = random.choice(list(deg_to_rad.keys()))
    answer = deg_to_rad[deg]
    question_text = f"請問 {deg}° 等於多少弧度 (radian)？ (請用 pi 表示，例如: pi/2)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
