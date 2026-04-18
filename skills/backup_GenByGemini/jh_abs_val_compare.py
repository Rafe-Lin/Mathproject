# skills/jh_abs_val_compare.py
import random

def generate(level=1):
    """
    生成一道「絕對值比較大小」的題目。
    """
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    while abs(a) == abs(b):
        b = random.randint(-10, 10)

    abs_a = abs(a)
    abs_b = abs(b)

    if abs_a > abs_b:
        correct_answer = ">"
    elif abs_a < abs_b:
        correct_answer = "<"
    else: # Should not happen due to while loop
        correct_answer = "="

    question_text = f"請比較 |{a}| 和 |{b}| 的大小。\n請在下方填入 >、< 或 =。"

    context_string = f"比較 |{a}| 和 |{b}| 的大小。"

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