import random

def generate_cubic_function_question():
    a = random.randint(1, 2)
    b = random.randint(-3, 3)
    c = random.randint(-5, 5)
    d = random.randint(-9, 9)
    x_val = random.randint(-2, 2)

    # Function: f(x) = ax^3 + bx^2 + cx + d
    correct_answer = a * (x_val**3) + b * (x_val**2) + c * x_val + d

    question_text = f"已知三次函數 f(x) = {a}x^3 + {b}x^2 + {c}x + {d}，求 f({x_val}) 的值。"

    return {
        "text": question_text,
        "answer": str(correct_answer),
        "validation_function_name": None
    }
