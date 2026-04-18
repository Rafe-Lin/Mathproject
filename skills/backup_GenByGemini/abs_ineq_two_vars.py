import random

def generate(level=1):
    """
    生成一道「絕對值不等式 (多項)」的題目。
    |x-a| + |x-b| < c
    """
    a = random.randint(-5, 0)
    b = random.randint(1, 5)
    dist = b - a
    c = random.randint(dist + 1, dist + 5)
    
    op_char = random.choice(['<', '<='])
    
    question_text = f"請求解絕對值不等式：|x - {a}| + |x - {b}| {op_char} {c}"
    
    # 解 |x-a|+|x-b|=c => x = (a+b±c)/2
    sol1 = (a + b - c) / 2
    sol2 = (a + b + c) / 2
    
    correct_answer = f"{sol1} {op_char} x {op_char} {sol2}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.replace(" ", "")
    correct = correct_answer.replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text}