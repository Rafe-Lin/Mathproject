# \坐標與函數\絕對值不等式 (大於基本型)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「絕對值不等式 (大於基本型)」的題目。
    """
    c = random.randint(1, 20)
    a = random.randint(1, 5)
    question_text = f"請求解不等式 |x - {a}| > {c}。"
    correct_answer = f"x>{a+c}或x<{a-c}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)