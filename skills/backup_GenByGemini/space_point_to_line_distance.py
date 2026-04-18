import random
import numpy as np

def generate(level=1):
    """
    生成一道「空間中點到直線距離」的題目。
    """
    # 直線 L: P₀ + tv
    p0 = np.array([random.randint(-3, 3) for _ in range(3)])
    v = np.array([random.randint(1, 3) for _ in range(3)])
    # 線外一點 Q
    q = p0 + np.array([random.randint(-5,5), random.randint(-5,5), random.randint(-5,5)])
    
    question_text = f"請求出點 Q{tuple(q)} 到直線 L: (x,y,z) = {tuple(p0)} + t*{tuple(v)} 的距離。(四捨五入至小數點後一位)"
    
    # dist = |(Q-P₀) × v| / |v|
    qp0 = q - p0
    dist = np.linalg.norm(np.cross(qp0, v)) / np.linalg.norm(v)
    correct_answer = str(round(dist, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = abs(float(user) - float(correct)) < 0.1
    result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}