# \積分\定積分定義 (黎曼和)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「定積分定義 (黎曼和)」的觀念題。
    """
    question_text = (
        "定積分 ∫[a,b] f(x)dx 在幾何上的意義是什麼？\n\n"
        "A) 函數 f(x) 在 x=b 的切線斜率\n"
        "B) 函數 f(x) 的圖形與 x 軸在 [a, b] 區間所圍成的「有向」面積\n"
        "C) 函數 f(x) 在 [a, b] 區間的平均值"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')