# \函數\對數換底公式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「對數換底公式」的題目。
    """
    if level == 1:
        question_text = (
            "根據對數的換底公式，log_a(b) 可以轉換為以 c 為底的對數，其形式為何？\n\n"
            "A) log_c(b) / log_c(a)\n"
            "B) log_c(a) / log_c(b)\n"
            "C) log_b(c) / log_a(c)"
        )
        correct_answer = "A"
    else: # level 2
        a, b = random.randint(2, 5), random.randint(2, 5)
        question_text = f"請計算 log_{a}({b}) * log_{b}({a}) 的值。"
        correct_answer = "1"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        return check_answer(user_answer, correct_answer, check_type='numeric')