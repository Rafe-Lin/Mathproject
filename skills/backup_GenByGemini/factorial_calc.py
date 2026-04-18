import random
import math

def generate(level=1):
    """
    生成一道「階乘計算」的題目。
    level 1: n!
    level 2: n! / m!
    """
    if level == 1:
        n = random.randint(4, 6)
        question_text = f"請計算 {n}! 的值。"
        correct_answer = str(math.factorial(n))
    else: # level 2
        n = random.randint(5, 8)
        m = random.randint(2, n - 2)
        question_text = f"請計算 {n}! / {m}! 的值。"
        correct_answer = str(math.factorial(n) // math.factorial(m))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}