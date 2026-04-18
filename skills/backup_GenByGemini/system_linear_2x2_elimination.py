# \方程式\加減消去法 (二元)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「加減消去法 (二元)」的題目。
    """
    # 預設一組整數解
    x_sol, y_sol = random.randint(-5, 5), random.randint(-5, 5)

    # 構造係數
    a1, b1 = random.randint(1, 4), random.randint(1, 4)
    if level == 1:
        # level 1: 讓其中一個係數相同或互為相反數
        a2 = a1 * random.choice([1, -1])
        b2 = random.randint(1, 4)
        while a1*b2 - a2*b1 == 0: # 避免無限多解或無解
            b2 = random.randint(1, 4)
    else: # level 2: 一般情況
        a2, b2 = random.randint(1, 4), random.randint(1, 4)
        while a1*b2 - a2*b1 == 0:
            b2 = random.randint(1, 4)

    c1 = a1*x_sol + b1*y_sol
    c2 = a2*x_sol + b2*y_sol

    question_text = f"請利用加減消去法，求解下列聯立方程式的解 (x, y)：\n{a1}x + {b1}y = {c1}\n{a2}x + {b2}y = {c2}"
    correct_answer = f"({x_sol},{y_sol})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)