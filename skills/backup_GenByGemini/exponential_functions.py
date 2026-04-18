import random

def generate_exponential_functions_question():
    """動態生成一道「指數函數」的題目 (解方程式)"""
    base = random.randint(2, 5)
    exponent = random.randint(2, 4)
    result = base ** exponent
    question_text = f"解指數方程式 {base}^x = {result}，請問 x = ?"
    answer = str(exponent)
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
