# \微分應用\反曲點
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「反曲點」的觀念題。
    """
    question_text = (
        "若點 (c, f(c)) 是函數 f(x) 圖形的一個反曲點，則下列敘述何者「最可能」正確？\n\n"
        "A) f'(c) = 0\n"
        "B) f''(c) = 0\n"
        "C) f(c) = 0"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')