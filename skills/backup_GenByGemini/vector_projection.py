import random
import numpy as np

def generate(level=1):
    """
    生成一道「平面向量正射影」的題目。
    """
    a = np.array([random.randint(-5, 5) for _ in range(2)])
    b = np.array([random.randint(-3, 3) for _ in range(2)])
    while np.all(b==0): b = np.array([random.randint(-3, 3) for _ in range(2)])

    if level == 1:
        question_text = f"請求出向量 a = {tuple(a)} 在向量 b = {tuple(b)} 上的「正射影長」。(四捨五入至小數點後一位)"
        proj_len = abs(np.dot(a, b)) / np.linalg.norm(b)
        correct_answer = str(round(proj_len, 1))
    else: # level 2
        question_text = f"請求出向量 a = {tuple(a)} 在向量 b = {tuple(b)} 上的「正射影向量」。(坐標四捨五入至小數點後一位)"
        # proj_b(a) = (a·b / |b|²) * b
        proj_vec = (np.dot(a, b) / np.dot(b, b)) * b
        proj_vec_rounded = [round(c, 1) for c in proj_vec]
        correct_answer = str(tuple(proj_vec_rounded))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}