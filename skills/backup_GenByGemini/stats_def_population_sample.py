# \統計\母體與樣本
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「母體與樣本」的觀念題。
    """
    if level == 1:
        question_text = (
            "為了了解某高中全體高三學生的數學平均成績，隨機抽取了 100 位學生進行測驗。請問在這個調查中，「母體」是什麼？\n\n"
            "A) 被抽出的 100 位學生\n"
            "B) 某高中全體高三學生\n"
            "C) 100 位學生的數學成績"
        )
        correct_answer = "B"
    else: # level 2
        question_text = (
            "政府每十年會對全國所有家庭進行戶口和住宅普查，以收集詳細的人口資料。這種調查方法稱為什麼？\n\n"
            "A) 抽樣調查 (Sampling Survey)\n"
            "B) 普查 (Census)\n"
            "C) 實驗設計 (Experimental Design)"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')