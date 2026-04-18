# skills/jh_equation_solve_with_parentheses.py
import random

def generate(level=1):
    """
    生成一道「解含括號的一元一次方程式」的題目。
    a(bx + c) = d
    """
    x = random.randint(-5, 5)
    a = random.randint(-5, 5)
    while a == 0 or a == 1:
        a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    while b == 0:
        b = random.randint(-5, 5)
    c = random.randint(-5, 5)

    d = a * (b * x + c)

    c_str = f"+ {c}" if c > 0 else f"- {abs(c)}" if c < 0 else ""
    question_text = f"請求解方程式：{a}({b}x {c_str}) = {d}"

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