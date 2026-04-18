# \直線方程式\直線方程式 (兩點式)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「直線方程式 (兩點式)」的題目。
    """
    p1 = (random.randint(-5, 5), random.randint(-5, 5))
    p2 = (random.randint(-5, 5), random.randint(-5, 5))
    while p1[0] == p2[0] or p1[1] == p2[1]: # 避免水平或垂直線
        p2 = (random.randint(-5, 5), random.randint(-5, 5))

    question_text = f"請求出通過點 {p1} 和 {p2} 的直線方程式。(寫成 y=mx+b 的形式)"
    
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    b = p1[1] - m * p1[0]
    
    correct_answer = f"y={m:.2f}x+{b:.2f}".replace("+-", "-")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)