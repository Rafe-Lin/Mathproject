# \函數\對數不等式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「對數不等式」的題目。
    """
    if level == 1: # a > 1
        base = random.randint(2, 4)
        val1 = random.randint(2, 5)
        val2 = random.randint(val1 + 1, 8)
        question_text = f"請求解不等式：log_{base}({val1}) < log_{base}(x)"
        correct_answer = f"x > {val1}"
    else: # 0 < a < 1
        base = f"1/{random.randint(2, 4)}"
        val1 = random.randint(2, 5)
        val2 = random.randint(val1 + 1, 8)
        question_text = f"請求解不等式：log_({base})({val1}) < log_({base})(x)"
        correct_answer = f"0 < x < {val1}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)