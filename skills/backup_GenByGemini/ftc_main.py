# \積分\微積分基本定理 (d/dx)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「微積分基本定理」的觀念題。
    """
    question_text = (
        "根據微積分第一基本定理，若 F(x) = ∫[a,x] f(t)dt，則 F'(x) 等於什麼？\n\n"
        "A) f(x)\n"
        "B) f(a)\n"
        "C) f(x) - f(a)"
    )
    correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')