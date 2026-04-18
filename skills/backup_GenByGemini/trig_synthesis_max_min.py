# \三角函數\利用疊合求最大最小值
import random
import math

def generate(level=1):
    """
    生成一道「利用疊合求最大最小值」的題目。
    """
    if level == 1:
        a, b = 1, 1
        question_text = "請求出函數 f(x) = sin(x) + cos(x) 的最大值。"
        # r = sqrt(a²+b²)
        correct_answer = "√2"
    else: # level 2
        a = random.choice([3, 5, 8])
        b = random.choice([4, 12, 15])
        question_text = f"請求出函數 f(x) = {a}sin(x) - {b}cos(x) 的最小值。"
        r = math.sqrt(a*a + b*b)
        correct_answer = f"-{int(r)}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}