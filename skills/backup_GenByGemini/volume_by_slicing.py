import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「體積 (切片法)」的觀念題。
    """
    question_text = (
        "利用切片法計算一個立體在 [a, b] 區間的體積時，其基本公式為何？ (A(x)為在 x 處的截面積)\n\n"
        "A) V = ∫[a,b] A(x) dx\n"
        "B) V = A(b) - A(a)\n"
        "C) V = π ∫[a,b] A(x) dx"
    )
    correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')