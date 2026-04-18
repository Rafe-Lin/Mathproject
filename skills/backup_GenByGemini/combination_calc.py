import random
import math

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate(level=1):
    """
    生成一道「組合計算」的題目。
    level 1: C(n, k)
    level 2: C(n, k) + C(m, l)
    """
    if level == 1:
        n = random.randint(5, 10)
        k = random.randint(2, n - 2)
        question_text = f"請計算 C({n}, {k}) 的值。"
        correct_answer = str(C(n, k))
    else: # level 2
        n1, k1 = random.randint(5, 7), 2
        n2, k2 = random.randint(4, 6), 2
        question_text = f"請計算 C({n1}, {k1}) + C({n2}, {k2}) 的值。"
        correct_answer = str(C(n1, k1) + C(n2, k2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}