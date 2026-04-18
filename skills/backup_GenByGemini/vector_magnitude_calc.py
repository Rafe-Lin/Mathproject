import random
import math

def generate(level=1):
    """
    生成一道「平面向量的長度」的題目。
    """
    if level == 1:
        # 使用畢氏三元數
        a, b, c = random.choice([(3,4,5), (6,8,10), (5,12,13)])
        vec = random.sample([a,b], 2)
    else: # level 2
        vec = [random.randint(-10, 10) for _ in range(2)]

    question_text = f"請求出向量 v = {tuple(vec)} 的長度（大小）。"
    mag = math.sqrt(vec[0]**2 + vec[1]**2)
    correct_answer = str(int(mag))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}