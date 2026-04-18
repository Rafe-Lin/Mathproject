import random
import numpy as np

def generate(level=1):
    """
    生成一道「直線與平面交點」的題目。
    """
    # 構造直線
    point = np.array([random.randint(-3, 3) for _ in range(3)])
    direction = np.array([random.randint(1, 3) for _ in range(3)])
    # 構造平面
    normal = np.array([random.randint(1, 3) for _ in range(3)])
    d = random.randint(-5, 5)
    
    # 將參數式代入平面方程式解 t
    # n·(p+vt) + d = 0 => n·p + (n·v)t + d = 0 => t = -(n·p+d)/(n·v)
    t = -(np.dot(normal, point) + d) / np.dot(normal, direction)
    intersection_point = point + direction * t
    
    question_text = f"請求出直線 L: (x,y,z) = {tuple(point)} + t*{tuple(direction)} 與平面 E: {normal[0]}x+{normal[1]}y+{normal[2]}z+{d}=0 的交點坐標。"
    correct_answer = str(tuple(round(c, 1) for c in intersection_point))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}