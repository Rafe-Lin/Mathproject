import random
import numpy as np

def generate(level=1):
    """
    生成一道「行列式與平行六面體體積」的題目。
    """
    if level == 1:
        v1 = [random.randint(1, 5), 0, 0]
        v2 = [0, random.randint(1, 5), 0]
        v3 = [0, 0, random.randint(1, 5)]
    else: # level 2
        v1 = [random.randint(-5, 5), random.randint(-5, 5), 0]
        v2 = [random.randint(-5, 5), 0, random.randint(-5, 5)]
        v3 = [0, random.randint(-5, 5), random.randint(-5, 5)]

    question_text = f"由向量 a={tuple(v1)}, b={tuple(v2)}, c={tuple(v3)} 所張出的平行六面體，其體積為何？"
    volume = abs(np.linalg.det(np.array([v1, v2, v3])))
    correct_answer = str(round(volume))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}