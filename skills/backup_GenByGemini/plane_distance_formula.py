# \坐標與函數\平面兩點距離
import random
import math
from .utils import check_answer

def generate(level=1):
    """
    生成一道「平面兩點距離」的題目。
    """
    if level == 1:
        # 使用畢氏三元數讓答案是整數
        dx, dy, dist = random.choice([(3,4,5), (6,8,10), (5,12,13), (8,15,17)])
        p1 = (random.randint(-10, 10), random.randint(-10, 10))
        p2 = (p1[0] + dx, p1[1] + dy)
        correct_answer = str(dist)
    else: # level 2, 答案可能帶根號
        p1 = (random.randint(-10, 10), random.randint(-10, 10))
        p2 = (random.randint(-10, 10), random.randint(-10, 10))
        dist_sq = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
        correct_answer = f"√{dist_sq}"
    question_text = f"請求出平面上兩點 P₁{p1} 與 P₂{p2} 之間的距離。"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("sqrt", "√")
    return check_answer(user_answer, correct_answer)