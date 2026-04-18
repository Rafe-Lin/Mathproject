# \複數\複數的 n 次方根
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「複數的 n 次方根」的觀念題。
    """
    n = random.randint(3, 8)
    if level == 1:
        question_text = f"請問方程式 z^{n} = 1 在複數平面上共有幾個根？"
        correct_answer = str(n)
    else: # level 2
        question_text = f"方程式 z^{n} = 1 的 {n} 個根，在複數平面上所形成的圖形為何？\n\n" \
                        f"A) 一條直線\nB) 一個圓\nC) 一個內接於單位圓的正{n}邊形"
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')