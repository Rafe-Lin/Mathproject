# \多項式\解分式方程式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「解分式方程式」的題目。
    """
    if level == 1:
        # 構造 1/(x-a) = c
        a = random.randint(1, 5)
        c = random.choice([1, 2, 0.5, 0.25])
        question_text = f"請求解分式方程式： 1/(x - {a}) = {c}"
        # 1 = c(x-a) => 1/c = x-a => x = a + 1/c
        correct_answer = str(a + 1/c)
    else: # level 2
        # 構造 1/(x-a) + 1/(x-b) = 0
        a = random.randint(1, 5)
        b = random.randint(6, 10)
        question_text = f"請求解分式方程式： 1/(x - {a}) + 1/(x - {b}) = 0"
        # (x-b) + (x-a) = 0 => 2x = a+b => x = (a+b)/2
        correct_answer = str((a+b)/2)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')