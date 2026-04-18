import random

def generate_polynomial_inequality_question():
    # Simple linear inequality for now
    a = random.randint(-5, 5)
    while a == 0:
        a = random.randint(-5, 5)
    b = random.randint(-10, 10)
    
    sign = random.choice(['>', '<', '>=', '<='])

    question_text = f"解不等式 {a}x {sign} {b}。"
    
    # Solve for x
    if a > 0:
        if sign == '>': answer_sign = '>'
        elif sign == '<': answer_sign = '<'
        elif sign == '>=': answer_sign = '>='
        else: answer_sign = '<='
        answer_val = b / a
    else: # a < 0, reverse inequality sign
        if sign == '>': answer_sign = '<'
        elif sign == '<': answer_sign = '>'
        elif sign == '>=': answer_sign = '<='
        else: answer_sign = '>='
        answer_val = b / a
    
    # Format answer to one decimal place if not integer
    if answer_val == int(answer_val):
        answer = f"x {answer_sign} {int(answer_val)}"
    else:
        answer = f"x {answer_sign} {answer_val:.1f}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
