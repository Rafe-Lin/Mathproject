# \函數\指數大小比較
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「指數大小比較」的題目。
    """
    if level == 1: # 同底
        base = random.randint(2, 5)
        exp1 = random.uniform(1.1, 2.5)
        exp2 = random.uniform(2.6, 4.0)
        question_text = f"請比較 A = {base}^{exp1:.1f} 與 B = {base}^{exp2:.1f} 的大小。"
        correct_answer = "A < B"
    else: # level 2, 不同底
        base1 = 2
        base2 = 3
        exp1 = random.randint(3, 5)
        exp2 = random.randint(2, 3)
        question_text = f"請比較 A = {base1}^{exp1} 與 B = {base2}^{exp2} 的大小。"
        correct_answer = "A > B" if base1**exp1 > base2**exp2 else "A < B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)