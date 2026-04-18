# \微分應用\函數凹向 (f'')
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「函數凹向 (f'')」的觀念題。
    """
    if level == 1:
        question_text = (
            "若函數 f(x) 的二階導函數 f''(x) 在區間 (a, b) 上恆為正，則 f(x) 在此區間的圖形凹向為何？\n\n"
            "A) 凹向上 (像碗公)\nB) 凹向下 (像蓋子)\nC) 沒有凹向性"
        )
        correct_answer = "A"
    else: # level 2
        question_text = (
            "若函數 f(x) 的二階導函數 f''(x) 在區間 (a, b) 上恆為負，則 f(x) 在此區間的圖形凹向為何？\n\n"
            "A) 凹向上 (像碗公)\nB) 凹向下 (像蓋子)\nC) 沒有凹向性"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')