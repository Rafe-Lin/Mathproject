# \函數\對數方程式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「對數方程式」的題目。
    """
    base = random.randint(2, 5)
    if level == 1:
        val = random.randint(2, 4)
        x = base ** val
        question_text = f"請求解方程式：log_{base}(x) = {val}"
        correct_answer = str(x)
    else: # level 2
        x1, x2 = random.randint(2, 5), random.randint(2, 5)
        question_text = f"請求解方程式：log_{base}(x) = log_{base}({x1}) + log_{base}({x2})"
        correct_answer = str(x1 * x2)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')