# \圓錐曲線\橢圓參數式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「橢圓參數式」的觀念題。
    """
    a, b = random.randint(2,10), random.randint(2,10)
    while a==b: b = random.randint(2,10)
    question_text = (
        f"橢圓方程式為 x²/{a*a} + y²/{b*b} = 1，其參數式可以表示為下列何者？ (θ為參數)\n\n"
        f"A) x = {a}sinθ, y = {b}cosθ\n"
        f"B) x = {a}cosθ, y = {b}sinθ\n"
        f"C) x = {a*a}cosθ, y = {b*b}sinθ"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')