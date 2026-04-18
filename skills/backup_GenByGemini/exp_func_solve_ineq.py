# \函數\指數不等式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「指數不等式」的題目。
    """
    if level == 1: # a > 1
        base = random.randint(2, 4)
        exp1 = random.randint(2, 5)
        exp2 = random.randint(exp1 + 1, 8)
        question_text = f"請求解不等式：{base}^{exp1} < {base}ˣ"
        correct_answer = f"x > {exp1}"
    else: # 0 < a < 1
        base = f"1/{random.randint(2, 4)}"
        exp1 = random.randint(2, 5)
        exp2 = random.randint(exp1 + 1, 8)
        question_text = f"請求解不等式：({base})^{exp1} < ({base})ˣ"
        correct_answer = f"x < {exp1}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)