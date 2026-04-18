# skills/jh_integer_compare.py
import random

def generate(level=1):
    """
    生成一道「整數比較大小」的題目。
    """
    num1 = random.randint(-10, 10)
    num2 = random.randint(-10, 10)
    while num1 == num2:
        num2 = random.randint(-10, 10)

    if num1 > num2:
        correct_answer = ">"
    else:
        correct_answer = "<"

    question_text = f"請比較 {num1} 和 {num2} 的大小。\n請在下方填入 >、< 或 =。"

    context_string = f"在數線上，越右邊的數越大。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    if user == correct:
        is_correct = True
        result_text = f"完全正確！答案是 {correct}。"
    else:
        is_correct = False
        result_text = f"答案不正確。正確答案是：{correct}"

    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": is_correct
    }