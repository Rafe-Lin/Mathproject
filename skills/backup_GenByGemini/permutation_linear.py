import random
import math

def P(n, k):
    return math.factorial(n) // math.factorial(n - k)

def generate(level=1):
    """
    生成一道「直線排列」的題目。
    level 1: n 個人排成一列。
    level 2: n 個人選 k 個人排成一列。
    """
    n = random.randint(4, 6)
    if level == 1:
        question_text = f"{n} 個人排成一列，共有多少種排法？"
        correct_answer = str(math.factorial(n))
    else: # level 2
        k = random.randint(2, n - 1)
        question_text = f"從 {n} 個人中選出 {k} 人排成一列，共有多少種排法？"
        correct_answer = str(P(n, k))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}