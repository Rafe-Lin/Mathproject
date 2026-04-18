# skills/jh_inequality_solve_multi_step.py
import random

def generate(level=1):
    """
    生成一道「解一元一次不等式 (多步)」的題目。
    """
    x_boundary = random.randint(-5, 5)
    a = random.randint(-4, 4)
    while a == 0 or a == 1: a = random.randint(-4, 4)
    b = random.randint(-10, 10)
    
    op_ineq = random.choice(['>', '<', '>=', '<='])
    
    c = a * x_boundary + b
    
    question_text = f"請求解不等式：{a}x + {b} {op_ineq} {c}"

    # 處理乘以/除以負數時不等號變向
    if a < 0:
        op_map = {'>': '<', '<': '>', '>=': '<=', '<=': '>='}
        final_op = op_map[op_ineq]
    else:
        final_op = op_ineq
        
    correct_answer = f"x{final_op}{x_boundary}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": f"解不等式，注意同乘以或同除以一個負數時，不等號要變向。"
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}