import random
import math

def generate(level=1):
    """
    生成一道「柯西不等式」的應用題。
    (a₁b₁ + a₂b₂)² ≤ (a₁² + a₂²)(b₁² + b₂²)
    """
    a, b = random.randint(1, 5), random.randint(1, 5)
    k = random.randint(5, 10)
    question_text = f"已知 x, y 為實數，且 x² + y² = {k*k}，求 {a}x + {b}y 的最大值。"
    # (ax+by)² <= (a²+b²)(x²+y²)
    max_val = math.sqrt((a*a+b*b) * (k*k))
    correct_answer = str(round(max_val))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}