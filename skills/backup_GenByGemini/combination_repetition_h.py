import random
import math

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def H(n, k):
    return C(n + k - 1, k)

def generate(level=1):
    """
    生成一道「重複組合」的題目。
    level 1: x+y+z = n (非負整數解)
    level 2: x+y+z = n (正整數解)
    """
    n = random.randint(5, 10)
    k = 3
    if level == 1:
        question_text = f"方程式 x + y + z = {n} 的非負整數解共有幾組？"
        correct_answer = str(H(k, n))
    else: # level 2
        question_text = f"方程式 x + y + z = {n} 的正整數解共有幾組？"
        correct_answer = str(H(k, n - k))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}