# skills/jh_inequality_solve_mul_div_negative.py
import random

def generate(level=1):
    """
    生成一道「解一元一次不等式 (乘除負數)」的題目。
    """
    x_boundary = random.randint(-5, 5)
    a = random.randint(-5, -2) # 確保是負數
    
    op_ineq = random.choice(['>', '<', '>=', '<='])
    
    c = a * x_boundary
    
    question_text = f"請求解不等式：{a}x {op_ineq} {c}"

    # 處理不等號變向
    op_map = {'>': '<', '<': '>', '>=': '<=', '<=': '>='}
    final_op = op_map[op_ineq]
        
    correct_answer = f"x{final_op}{x_boundary}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": f"解不等式時，當兩邊同乘以或同除以一個「負數」，不等號的方向要改變。"
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