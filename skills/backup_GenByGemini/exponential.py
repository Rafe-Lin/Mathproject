import random

def generate_exponential_question():
    base = random.randint(2, 5)
    exponent = random.randint(2, 4)
    correct_answer = base ** exponent
    question_text = f"計算 {base}^{exponent} = ?"
    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": None
    }
