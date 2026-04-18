# \坐標與函數\數線中點公式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「數線中點公式」的題目。
    """
    a = random.randint(-20, 0)
    b = random.randint(1, 20)
    
    if level == 1:
        # 確保中點為整數
        if (a + b) % 2 != 0:
            b += 1
        question_text = f"請問數線上兩點 A({a}) 與 B({b}) 的中點坐標為何？"
        correct_answer = str((a + b) / 2)
    else: # level 2, 逆向提問
        midpoint = random.randint(-5, 5)
        correct_answer = str(2 * midpoint - a)
        question_text = f"已知數線上兩點 A({a}) 與 M({midpoint})，若 M 為線段 AB 的中點，請問 B 點的坐標為何？"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')