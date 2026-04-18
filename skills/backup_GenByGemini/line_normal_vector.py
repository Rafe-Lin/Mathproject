# \向量\直線的法向量
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「直線的法向量」的題目。
    """
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    c = random.randint(-10, 10)
    line_eq = f"{a}x + {b}y + {c} = 0"

    if level == 1:
        # 正向提問：給定方程式，求法向量
        question_text = f"請問直線 L: {line_eq} 的一個法向量為何？"
        correct_answer = f"({a},{b})"
    else: # level 2, 逆向提問
        # 給定法向量和一個點，求直線方程式
        p = (random.randint(-5, 5), random.randint(-5, 5))
        # a(x-px) + b(y-py) = 0 => ax + by - (a*px + b*py) = 0
        c_new = - (a * p[0] + b * p[1])
        question_text = f"已知直線 L 的法向量為 ({a},{b}) 且通過點 {p}，請問直線 L 的方程式為何？ (寫成 ax+by+c=0 的形式)"
        correct_answer = f"{a}x+{b}y+{c_new}=0".replace("+-", "-")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)