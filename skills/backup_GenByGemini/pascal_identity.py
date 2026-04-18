import random
import math

def C(n, k):
    if k < 0 or k > n: return 0
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate(level=1):
    """
    生成一道「巴斯卡定理」的題目。
    C(n, k) = C(n-1, k-1) + C(n-1, k)
    level 1: 直接計算
    level 2: 觀念題
    """
    n = random.randint(5, 10)
    k = random.randint(2, n - 2)
    if level == 1:
        question_text = f"請計算 C({n-1}, {k-1}) + C({n-1}, {k}) 的值。"
        correct_answer = str(C(n, k))
    else: # level 2
        question_text = f"根據巴斯卡定理，C({n}, {k}) 可以拆解為哪兩項之和？\n(格式: C(a,b)+C(c,d))"
        correct_answer = f"C({n-1},{k-1})+C({n-1},{k})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}