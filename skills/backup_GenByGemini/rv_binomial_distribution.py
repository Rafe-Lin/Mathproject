# \機率統計\二項分布
import random
import math
from fractions import Fraction

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate(level=1):
    """
    生成一道「二項分布」的題目。
    """
    n = random.randint(3, 5)
    p = Fraction(1, random.randint(2, 4))
    if level == 1:
        k = random.randint(1, n-1)
        question_text = f"重複擲一顆不公正的硬幣 {n} 次，每次出現正面的機率為 {p}。請問恰好出現 {k} 次正面的機率是多少？ (請以最簡分數 a/b 表示)"
    else: # level 2
        k = random.randint(n-1, n)
        question_text = f"某射手命中率為 {p}，連續射擊 {n} 次。請問他「至少」命中 {k} 次的機率是多少？ (請以最簡分數 a/b 表示)"
    
    ans = sum(C(n, i) * (p**i) * ((1-p)**(n-i)) for i in range(k, n + 1))
    correct_answer = f"{ans.numerator}/{ans.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}