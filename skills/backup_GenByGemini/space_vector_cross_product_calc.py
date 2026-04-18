import random
import numpy as np

def generate(level=1):
    """
    生成一道「空間向量外積」的計算題。
    """
    if level == 1:
        v1 = [random.randint(0, 5) for _ in range(3)]
        v2 = [random.randint(0, 5) for _ in range(3)]
    else: # level 2
        v1 = [random.randint(-5, 5) for _ in range(3)]
        v2 = [random.randint(-5, 5) for _ in range(3)]

    question_text = f"已知向量 a = {tuple(v1)}，向量 b = {tuple(v2)}，請求出其外積 a × b。"
    cross_product = np.cross(v1, v2)
    correct_answer = str(tuple(cross_product))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}