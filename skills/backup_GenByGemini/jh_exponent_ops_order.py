# skills/jh_exponent_ops_order.py
import random

def generate(level=1):
    """
    生成一道「指數的四則運算」的題目。
    """
    num1 = random.randint(2, 5)
    exp1 = random.randint(2, 3)
    num2 = random.randint(2, 5)
    op = random.choice(['+', '-', '*', '/'])

    if op == '+':
        question_text = f"請問 {num1}^{exp1} + {num2} 的值是多少？"
        correct_answer = str(num1**exp1 + num2)
    elif op == '-':
        question_text = f"請問 {num1}^{exp1} - {num2} 的值是多少？"
        correct_answer = str(num1**exp1 - num2)
    elif op == '*':
        question_text = f"請問 {num1}^{exp1} * {num2} 的值是多少？"
        correct_answer = str(num1**exp1 * num2)
    else: # op == '/'
        # 確保能整除
        res = num1**exp1
        divisor = random.randint(2, 5)
        res *= divisor
        num1, exp1 = num1, exp1 # just to be clear
        question_text = f"請問 {res} / {num1}^{exp1} 的值是多少？"
        correct_answer = str(divisor)

    context_string = f"遵循先乘方、後乘除、再加減的運算順序"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}