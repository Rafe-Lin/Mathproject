import random

def generate_trig_sum_difference_question():
    """動態生成一道「三角的和差角公式」的題目 (概念)"""
    formulas = {
        "sin(A+B)": "sin(A)cos(B)+cos(A)sin(B)",
        "sin(A-B)": "sin(A)cos(B)-cos(A)sin(B)",
        "cos(A+B)": "cos(A)cos(B)-sin(A)sin(B)",
        "cos(A-B)": "cos(A)cos(B)+sin(A)sin(B)"
    }
    func = random.choice(list(formulas.keys()))
    answer = formulas[func]
    question_text = f"請問 {func} 的展開式是什麼？(請用 sin(A), cos(B) 等方式作答)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
