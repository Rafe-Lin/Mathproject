import random

def generate_logarithmic_functions_question():
    """動態生成一道「對數函數」的題目 (解方程式)"""
    base = random.choice([2, 3, 5])
    result_exp = random.randint(2, 4)
    x = base ** result_exp
    question_text = f"解對數方程式 log{base}(x) = {result_exp}，請問 x = ?"
    answer = str(x)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
