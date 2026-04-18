import random
import numpy as np

def generate(level=1):
    """
    生成一道「過三點求平面方程式」的題目。
    """
    # 構造不共線的三點
    p1 = np.array([random.randint(-3, 3) for _ in range(3)])
    v1 = np.array([random.randint(1, 3), random.randint(1, 3), 0])
    v2 = np.array([random.randint(1, 3), 0, random.randint(1, 3)])
    p2 = p1 + v1
    p3 = p1 + v2
    
    question_text = f"請求出通過 A{tuple(p1)}, B{tuple(p2)}, C{tuple(p3)} 三點的平面方程式。(一般式 ax+by+cz+d=0)"
    
    # AB x AC 即為法向量
    normal = np.cross(v1, v2)
    # a(x-x1) + b(y-y1) + c(z-z1) = 0
    d = -np.dot(normal, p1)
    
    correct_answer = f"{normal[0]}x+{normal[1]}y+{normal[2]}z+{d}=0".replace("+-", "-").replace("1x","x")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}