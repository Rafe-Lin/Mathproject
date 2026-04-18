# \微分\除法規則
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「除法規則」的觀念題。
    """
    question_text = (
        "根據微分的除法規則，(f(x)/g(x))' 等於什麼？\n\n"
        "A) f'(x)/g'(x)\n"
        "B) (f'(x)g(x) + f(x)g'(x)) / [g(x)]²\n"
        "C) (f'(x)g(x) - f(x)g'(x)) / [g(x)]²"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')