import random

def generate_absolute_value_question():
    """動態生成一道「絕對值」的題目 (基本運算)"""
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    op = random.choice(['+', '-'])
    if op == '+':
        answer = abs(a) + abs(b)
    else:
        answer = abs(a) - abs(b)
    question_text = f"計算 |{a}| {op} |{b}| = ?"
    return {
        "text": question_text,
        "answer": str(answer),
        "validation_function_name": None
    }
