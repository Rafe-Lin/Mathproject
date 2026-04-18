import random
import numpy as np

def generate(level=1):
    """
    生成一道「兩歪斜線距離」的題目。
    """
    # 構造兩條歪斜線
    p1 = np.array([1, 0, 0])
    v1 = np.array([0, 1, 0]) # L1: y軸
    p2 = np.array([0, 0, random.randint(2,5)])
    v2 = np.array([1, 0, 1]) # L2
    
    question_text = f"請求出兩歪斜線 L₁: (x,y,z)={tuple(p1)}+t*{tuple(v1)} 與 L₂: (x,y,z)={tuple(p2)}+s*{tuple(v2)} 的距離。(四捨五入至小數點後一位)"
    
    # dist = |(P₂-P₁) · (v₁×v₂)| / |v₁×v₂|
    n = np.cross(v1, v2)
    p2p1 = p2 - p1
    dist = abs(np.dot(p2p1, n)) / np.linalg.norm(n)
    correct_answer = str(round(dist, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = abs(float(user) - float(correct)) < 0.1
    result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}