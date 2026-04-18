import random

def generate_trig_properties_laws_question():
    """動態生成一道「三角比的性質」的題目 (餘弦定理)"""
    a, b, angle_C, c = random.choice([(8, 3, 60, 7), (8, 5, 60, 7)])
    question_text = f"在三角形 ABC 中，若邊 a = {a}，邊 b = {b}，且兩邊的夾角 C = {angle_C}°，請問對邊 c 的長度是多少？"
    answer = str(c)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
