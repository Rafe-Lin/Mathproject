# \圓錐曲線\雙曲線漸近線
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「雙曲線漸近線」的題目。
    """
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    if level == 1:
        question_text = f"請問雙曲線 x²/{a*a} - y²/{b*b} = 1 的兩條漸近線方程式為何？"
        correct_answer = f"y=±({b}/{a})x"
    else: # level 2
        h, k = random.randint(-5, 5), random.randint(-5, 5)
        question_text = f"請問雙曲線 ((x-{h})²)/{a*a} - ((y-{k})²)/{b*b} = 1 的兩條漸近線交點（中心）為何？"
        correct_answer = f"({h},{k})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("^2", "²")
    return check_answer(user_answer, correct_answer)