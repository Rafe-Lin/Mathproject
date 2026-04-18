import random
import math

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate(level=1):
    """
    生成一道「組合性質」的題目。
    level 1: C(n, k) = C(n, n-k)
    level 2: 應用題
    """
    n = random.randint(10, 20)
    k = random.randint(2, 5)
    if level == 1:
        question_text = f"已知 C({n}, {k}) = {C(n, k)}，請問 C({n}, {n-k}) 的值是多少？"
        correct_answer = str(C(n, k))
    else: # level 2
        question_text = f"從 {n} 人中選出 {n-k} 人組隊，共有多少種選法？"
        correct_answer = str(C(n, n-k))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}