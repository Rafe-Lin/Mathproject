# \坐標與函數\絕對值方程式 (基本型)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「絕對值方程式 (基本型)」的題目。
    """
    c = random.randint(1, 20)
    a = random.randint(1, 5)
    question_text = f"請求解方程式 |x - {a}| = {c}。"
    correct_answer = f"{a+c},{a-c}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_parts = sorted(correct_answer.strip().split(','))
    return check_answer(",".join(user_parts), ",".join(correct_parts))