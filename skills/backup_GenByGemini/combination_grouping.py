import random
import math

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate(level=1):
    """
    生成一道「組合分堆」的題目。
    level 1: 分成兩堆。
    level 2: 分成三堆。
    """
    if level == 1:
        n = 6
        k1, k2 = 2, 4
        question_text = f"將 {n} 件不同的物品，依 {k1}, {k2} 分成兩堆，共有多少種分法？"
        correct_answer = str(C(n, k1))
    else: # level 2
        n = 9
        k1, k2, k3 = 2, 3, 4
        question_text = f"將 {n} 件不同的物品，依 {k1}, {k2}, {k3} 分成三堆，共有多少種分法？"
        correct_answer = str(C(n, k1) * C(n - k1, k2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}