# skills/jh_integer_ops_order.py
import random

def generate(level=1):
    """
    生成一道「整數的四則運算」題目。
    """
    num1 = random.randint(-9, 9)
    num2 = random.randint(-5, 5)
    while num2 == 0: num2 = random.randint(-5, 5)
    num3 = random.randint(-9, 9)

    ops = [random.choice(['+', '-']), random.choice(['*', '/'])]
    random.shuffle(ops)
    op1, op2 = ops

    # 確保除法可以整除
    if op1 == '/':
        num1 = num2 * random.randint(-5, 5)
    if op2 == '/':
        # 確保 num2 * num3 可以整除
        if op1 == '*':
            num3 = random.randint(-5, 5)
            while num3 == 0: num3 = random.randint(-5, 5)
            num2 = num3 * random.randint(-3, 3)
        else:
            num2 = num3 * random.randint(-3, 3)

    expr_str = f"{num1} {op1} {num2} {op2} {num3}"
    question_text = f"請計算：{expr_str}"
    
    correct_answer = str(eval(expr_str))

    context_string = "整數的四則運算，注意先乘除後加減，以及括號的優先級。"

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