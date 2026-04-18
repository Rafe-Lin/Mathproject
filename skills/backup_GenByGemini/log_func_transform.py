# \函數\對數函數圖形平移
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「對數函數圖形平移」的觀念題。
    """
    if level == 1:
        k = random.randint(2, 5)
        question_text = (
            f"函數 y = log₂(x) + {k} 的圖形，是由 y = log₂(x) 的圖形如何平移得到？\n\n"
            f"A) 向上平移 {k} 單位\nB) 向下平移 {k} 單位\nC) 向右平移 {k} 單位"
        )
        correct_answer = "A"
    else: # level 2
        h = random.randint(2, 5)
        question_text = (
            f"函數 y = log₃(x - {h}) 的圖形，是由 y = log₃(x) 的圖形如何平移得到？\n\n"
            f"A) 向左平移 {h} 單位\nB) 向右平移 {h} 單位\nC) 向上平移 {h} 單位"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')