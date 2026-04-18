# \積分\定積分性質
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「定積分性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於定積分的性質，∫[a,b] (f(x) + g(x))dx 等於什麼？\n\n"
            "A) (∫[a,b] f(x)dx) * (∫[a,b] g(x)dx)\n"
            "B) ∫[a,b] f(x)dx + ∫[a,b] g(x)dx\n"
            "C) ∫[a,b] f(x)dx - ∫[a,b] g(x)dx"
        )
        correct_answer = "B"
    else: # level 2
        a, b, c = sorted(random.sample(range(10), 3))
        question_text = f"已知 ∫[{a},{b}] f(x)dx = 5，∫[{b},{c}] f(x)dx = 3，請問 ∫[{a},{c}] f(x)dx 是多少？"
        correct_answer = "8"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        return check_answer(user_answer, correct_answer, check_type='numeric')