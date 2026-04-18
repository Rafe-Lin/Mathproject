import random
import math

def C(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate(level=1):
    """
    生成一道「二項式定理求特定項」的題目。
    """
    n = random.randint(4, 8)
    k = random.randint(1, n - 1)
    a = random.randint(2, 3)
    b = random.randint(2, 3)
    question_text = f"在 ({a}x+{b}y) 的 {n} 次方展開式中，請求出 x 的 {n-k} 次方、y 的 {k} 次方項的係數。".replace('^', '²' if n-k==2 else '³' if n-k==3 else '⁴' if n-k==4 else '⁵' if n-k==5 else '⁶' if n-k==6 else '⁷' if n-k==7 else '⁸')
    correct_answer = str(C(n, k) * (a**(n - k)) * (b**k))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}