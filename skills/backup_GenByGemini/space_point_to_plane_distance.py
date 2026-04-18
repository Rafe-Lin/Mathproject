import random
import numpy as np

def generate(level=1):
    """
    生成一道「點到平面距離」的題目。
    """
    point = np.array([random.randint(-5, 5) for _ in range(3)])
    if level == 1:
        # 讓分母漂亮
        normal = np.array(random.choice([[1,2,2], [2,3,6], [4,4,7]]))
    else:
        normal = np.array([random.randint(-4, 4) for _ in range(3)])
    d = random.randint(-10, 10)
    
    plane_eq = f"{normal[0]}x + {normal[1]}y + {normal[2]}z + {d} = 0"
    question_text = f"請求出點 P{tuple(point)} 到平面 E: {plane_eq} 的距離。(四捨五入至小數點後一位)"
    
    dist = abs(np.dot(normal, point) + d) / np.linalg.norm(normal)
    correct_answer = str(round(dist, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = abs(float(user) - float(correct)) < 0.1
    result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}