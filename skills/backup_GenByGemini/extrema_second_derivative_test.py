# \微分應用\二階導數檢定法 (極值)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「二階導數檢定法 (極值)」的觀念題。
    """
    if level == 1:
        question_text = (
            "若函數 f(x) 滿足 f'(c)=0 且 f''(c) < 0，則 f(c) 是什麼？\n\n"
            "A) 相對極大值\nB) 相對極小值\nC) 反曲點"
        )
        correct_answer = "A"
    else: # level 2
        question_text = (
            "若函數 f(x) 滿足 f'(c)=0 且 f''(c) > 0，則 f(c) 是什麼？\n\n"
            "A) 相對極大值\nB) 相對極小值\nC) 反曲點"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')