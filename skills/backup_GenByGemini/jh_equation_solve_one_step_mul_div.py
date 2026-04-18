# skills/jh_equation_solve_one_step_mul_div.py
import random

def generate(level=1):
    """
    生成一道「一元一次方程式 (一步乘除)」的題目。
    """
    x = random.randint(-10, 10)
    while x == 0:
        x = random.randint(-10, 10)
    a = random.randint(-5, 5)
    while a == 0 or a == 1:
        a = random.randint(-5, 5)
    
    op = random.choice(['*', '/'])
    
    if op == '*':
        c = a * x
        question_text = f"請求解方程式：{a}x = {c}"
    else: # op == '/'
        c = x
        x = a * c
        question_text = f"請求解方程式：x / {a} = {c}"

    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": f"解一元一次方程式 {question_text.split('：')[1].strip()}"
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace("x=", "")
    correct = correct_answer.strip()
    try:
        if float(user) == float(correct):
            is_correct = True
            result_text = f"完全正確！答案是 x = {correct}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：x = {correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：x = {correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}