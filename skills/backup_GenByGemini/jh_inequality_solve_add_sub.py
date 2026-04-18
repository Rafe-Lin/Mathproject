# skills/jh_inequality_solve_add_sub.py
import random

def generate(level=1):
    """
    生成一道「解一元一次不等式 (加減)」的題目。
    """
    x_boundary = random.randint(-10, 10)
    b = random.randint(-10, 10)
    while b == 0:
        b = random.randint(-10, 10)
    
    op_eq = random.choice(['+', '-'])
    op_ineq = random.choice(['>', '<', '>=', '<='])
    
    if op_eq == '+':
        c = x_boundary + b
        question_text = f"請求解不等式：x + {b} {op_ineq} {c}"
    else: # op_eq == '-'
        c = x_boundary - b
        question_text = f"請求解不等式：x - {b} {op_ineq} {c}"

    correct_answer = f"x{op_ineq}{x_boundary}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": f"利用等量公理移項解不等式。"
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}