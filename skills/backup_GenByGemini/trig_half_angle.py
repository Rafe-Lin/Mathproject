# \三角函數\半角公式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「半角公式」的題目。
    """
    if level == 1:
        question_text = (
            "根據餘弦的半角公式，cos²(θ/2) 等於什麼？\n\n"
            "A) (1 - cos(θ))/2\n"
            "B) (1 + cos(θ))/2\n"
            "C) 1 - cos(θ)"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "已知 cos(60°) = 1/2，請利用半角公式求出 cos(30°) 的值。"
        correct_answer = "√3/2"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        user_answer = user_answer.replace(" ", "").upper()
        return check_answer(user_answer, correct_answer.upper())