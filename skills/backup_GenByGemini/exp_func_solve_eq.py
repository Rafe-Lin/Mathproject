# \函數\指數方程式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「指數方程式」的題目。
    """
    base = random.randint(2, 5)
    if level == 1:
        exp = random.randint(2, 4)
        val = base ** exp
        question_text = f"請求解方程式：{base}ˣ = {val}"
        correct_answer = str(exp)
    else: # level 2
        exp1 = random.randint(2, 4)
        exp2 = random.randint(1, exp1-1)
        question_text = f"請求解方程式：{base}^(2x+1) = {base}^({exp1*2+1})"
        correct_answer = str(exp1)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')