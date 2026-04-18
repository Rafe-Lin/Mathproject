import random
import numpy as np
import math

def generate(level=1):
    """
    生成一道「兩平面夾角」的題目。
    """
    if level == 1:
        n1 = np.array([1, 1, 0])
        n2 = np.array([1, -1, 0])
        plane1_eq = "x + y + 3 = 0"
        plane2_eq = "x - y - 2 = 0"
    else: # level 2
        n1 = np.array([random.randint(-3, 3) for _ in range(3)])
        n2 = np.array([random.randint(-3, 3) for _ in range(3)])
        plane1_eq = f"{n1[0]}x+{n1[1]}y+{n1[2]}z+...=0"
        plane2_eq = f"{n2[0]}x+{n2[1]}y+{n2[2]}z+...=0"

    question_text = f"請求出兩平面 E₁: {plane1_eq} 與 E₂: {plane2_eq} 的夾角（銳角）的 cos 值。(四捨五入至小數點後兩位)"
    cos_angle = abs(np.dot(n1, n2)) / (np.linalg.norm(n1) * np.linalg.norm(n2))
    correct_answer = str(round(cos_angle, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = abs(float(user) - float(correct)) < 0.01
    result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}