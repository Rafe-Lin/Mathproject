# \函數\對數基本性質
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「對數基本性質」的題目。
    """
    base = random.randint(2, 10)
    if level == 1:
        prop = random.choice(['log_a(1)=0', 'log_a(a)=1'])
        if prop == 'log_a(1)=0':
            question_text = f"請求出 log_{base}(1) 的值。"
            correct_answer = "0"
        else:
            question_text = f"請求出 log_{base}({base}) 的值。"
            correct_answer = "1"
    else: # level 2, log(MN) = logM + logN
        m, n = random.randint(2, 5), random.randint(2, 5)
        question_text = f"請計算 log_{base}({m}) + log_{base}({n}) 的值，並以對數形式表示。"
        correct_answer = f"log_{base}({m*n})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer.lower())