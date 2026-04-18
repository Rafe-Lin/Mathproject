# \極限\函數的夾擠定理
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「函數的夾擠定理」的觀念題。
    """
    if level == 1:
        limit = random.randint(1, 5)
        question_text = f"已知在 x=a 附近，函數 f, g, h 滿足 f(x) ≤ g(x) ≤ h(x)。若已知 lim(x→a) f(x) = {limit} 且 lim(x→a) h(x) = {limit}，請問 lim(x→a) g(x) 是多少？"
        correct_answer = str(limit)
    else: # level 2
        question_text = "請求出函數 g(x) = x * sin(1/x) 在 x→0 時的極限值。"
        correct_answer = "0"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')