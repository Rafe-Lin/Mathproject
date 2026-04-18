# \積分應用\連續函數值的平均
import random

def generate(level=1):
    """
    生成一道「連續函數值的平均」的題目。
    """
    if level == 1:
        c = random.randint(10, 50)
        a, b = random.randint(0, 2), random.randint(3, 10)
        question_text = f"請求出常數函數 f(x) = {c} 在區間 [{a}, {b}] 上的平均值。"
        correct_answer = str(c)
    else: # level 2
        c = random.randint(2, 10)
        a, b = 0, random.randint(2, 6)
        question_text = f"請求出函數 f(x) = {c}x 在區間 [{a}, {b}] 上的平均值。"
        # (1/(b-a)) * ∫[a,b] cx dx = (1/b) * [c/2 * x²] from 0 to b = (1/b) * (c/2 * b²) = cb/2
        correct_answer = str(c * b / 2)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}