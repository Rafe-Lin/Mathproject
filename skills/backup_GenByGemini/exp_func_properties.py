# \函數\指數函數性質
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「指數函數性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於指數函數 y = aˣ (a>0, a≠1) 的圖形，下列敘述何者「恆正確」？\n\n"
            "A) 圖形必通過原點 (0,0)\n"
            "B) 圖形必通過點 (0,1)\n"
            "C) 圖形的 y 值恆為正"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "指數函數 y = aˣ (a>0, a≠1) 的圖形以哪一條直線為漸近線？\n\n" \
                        "A) x 軸 (y=0)\nB) y 軸 (x=0)\nC) 直線 y=x"
        correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')