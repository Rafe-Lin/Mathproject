import random

def generate_trig_graphs_periodicity_question():
    """動態生成一道「三角函數的圖形/週期性」的題目"""
    func = random.choice(['sin', 'cos'])
    b = random.choice([1, 2, 4])
    func_str = f"{func}({b}x)" if b != 1 else f"{func}(x)"
    if b == 1:
        answer = "2*pi"
    elif b == 2:
        answer = "pi"
    elif b == 4:
        answer = "pi/2"
    question_text = f"請問函數 f(x) = {func_str} 的最小正週期是多少？(答案請用 pi 表示，例如: 2*pi)"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
