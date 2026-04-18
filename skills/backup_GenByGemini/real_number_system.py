import random

def generate_real_number_system_question():
    """動態生成一道「數」的題目 (有理數/無理數)"""
    rational_examples = ["5", "-3", "1/2", "0.75"]
    irrational_examples = [("pi", "無理數"), ("sqrt(2)", "無理數")]
    if random.choice([True, False]):
        num_str = random.choice(rational_examples)
        answer = "有理數"
    else:
        num_str, answer = random.choice(irrational_examples)
    question_text = f"請問 {num_str} 是有理數還是無理數？"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
