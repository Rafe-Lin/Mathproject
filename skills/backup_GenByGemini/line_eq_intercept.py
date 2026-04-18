# \直線方程式\直線方程式 (截距式)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「直線方程式 (截距式)」的題目。
    """
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    while a == b: b = random.randint(1, 10)
    
    if level == 1:
        question_text = f"已知一直線的 x 截距為 {a}，y 截距為 {b}，請求出此直線的方程式。(寫成截距式)"
        correct_answer = f"x/{a}+y/{b}=1"
    else: # level 2
        question_text = f"已知一直線的 x 截距為 {a}，y 截距為 {b}，請問此直線是否通過點 ({a}, 0)？ (是/否)"
        correct_answer = "是"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)