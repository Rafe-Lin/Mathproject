import random
import math

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate(level=1):
    """
    生成一道「二項式定理展開」的題目。
    """
    a = random.randint(1, 3)
    b = random.randint(1, 3)
    n = 3
    question_text = f"請展開 ({a}x+{b}y) 的 {n} 次方。"
    c0 = a**3
    c1 = 3 * (a**2) * b
    c2 = 3 * a * (b**2)
    c3 = b**3
    correct_answer = f"{c0}x³ + {c1}x²y + {c2}xy² + {c3}y³"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}