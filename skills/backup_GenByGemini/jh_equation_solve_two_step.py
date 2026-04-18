# skills/jh_equation_solve_two_step.py
import random

def generate(level=1):
    """
    生成一道「一元一次方程式 (兩步)」的題目。
    ax + b = c
    """
    x = random.randint(-10, 10)
    a = random.randint(-5, 5)
    while a == 0 or a == 1:
        a = random.randint(-5, 5)
    b = random.randint(-10, 10)
    
    c = a * x + b
    
    b_str = f"+ {b}" if b > 0 else f"- {abs(b)}" if b < 0 else ""
    question_text = f"請求解方程式：{a}x {b_str} = {c}"

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