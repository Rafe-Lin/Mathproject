# skills/jh_integer_distributive_law.py
import random

def generate(level=1):
    """
    生成一道「整數分配律」的題目。
    """
    a = random.randint(-9, 9)
    while a == 0 or a == 1:
        a = random.randint(-9, 9)
    
    b = random.randint(-9, 9)
    c = random.randint(-9, 9)
    while b + c == 0:
        c = random.randint(-9, 9)

    # 隨機問 a*(b+c) 或 a*b + a*c
    if random.choice([True, False]):
        question_text = f"請計算 {a} × ( {b} + {c} ) 的值。"
    else:
        question_text = f"請計算 {a} × {b} + {a} × {c} 的值。"

    correct_answer = str(a * (b + c))

    context_string = f"利用分配律 a × (b + c) = a × b + a × c 進行計算。"

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

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}