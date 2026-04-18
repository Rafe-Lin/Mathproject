# \坐標與函數\垂直線檢驗法
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「垂直線檢驗法」的觀念題。
    """
    question_text = (
        "使用垂直線檢驗法時，如果一條垂直線與圖形交於「超過一個點」，這代表什麼？\n\n"
        "A) 該圖形是一個函數圖形\n"
        "B) 該圖形「不是」一個函數圖形\n"
        "C) 無法判斷"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')