# \微分\乘法規則
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「乘法規則」的觀念題。
    """
    question_text = (
        "根據微分的乘法規則，(f(x)·g(x))' 等於什麼？\n\n"
        "A) f'(x)·g'(x)\n"
        "B) f'(x)·g(x) + f(x)·g'(x)\n"
        "C) f'(x)·g(x) - f(x)·g'(x)"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')