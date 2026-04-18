import random

def generate_trig_ratios_right_triangle_question():
    """動態生成一道「直角三角形的三角比」的題目"""
    if random.choice([True, False]):
        a, b, c = 3, 4, 5
    else:
        a, b, c = 5, 12, 13
    leg1, leg2 = random.sample([a, b], 2)
    hypotenuse = c
    angle_choice = random.choice(['A', 'B'])
    trig_func = random.choice(['sin', 'cos', 'tan'])
    if angle_choice == 'A':
        angle_desc = f"對邊為 {leg1} 的那個銳角"
        if trig_func == 'sin':
            answer = f"{leg1}/{hypotenuse}"
        elif trig_func == 'cos':
            answer = f"{leg2}/{hypotenuse}"
        else:
            answer = f"{leg1}/{leg2}"
    else:
        angle_desc = f"對邊為 {leg2} 的那個銳角"
        if trig_func == 'sin':
            answer = f"{leg2}/{hypotenuse}"
        elif trig_func == 'cos':
            answer = f"{leg1}/{hypotenuse}"
        else:
            answer = f"{leg2}/{leg1}"
    question_text = f"在一個直角三角形中，兩股長分別為 {leg1} 和 {leg2}。請問 {angle_desc} 的 {trig_func} 值是多少？(請以 a/b 的形式表示)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
