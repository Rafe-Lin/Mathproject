# \多項式\分式四則運算
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「分式四則運算」的題目。
    """
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    
    if level == 1: # 加減
        question_text = f"請計算：1/(x-{a}) + 1/(x-{b})"
        correct_answer = f"(2x-{a+b})/((x-{a})(x-{b}))"
    else: # level 2, 乘除
        question_text = f"請計算：(x+{a})/(x-{b}) * (x-{b})/(x+{a})"
        correct_answer = "1"
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)