# \微分\可微分性
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「可微分性」的觀念題。
    """
    if level == 1:
        question_text = "若一個函數在某一點可微分，則它在該點是否必定連續？ (是/否)"
        correct_answer = "是"
    else: # level 2
        question_text = "函數 f(x) = |x| 在 x=0 處是否可微分？ (是/否)"
        correct_answer = "否"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')