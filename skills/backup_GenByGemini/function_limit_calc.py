# \極限\函數極限計算
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「函數極限計算」的題目。
    """
    if level == 1: # 因式分解
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        # (x-a)(x+b) / (x-a) = x+b
        num_str = f"x² + {b-a}x - {a*b}"
        den_str = f"x - {a}"
        question_text = f"請求出 lim (x→{a}) ({num_str}) / ({den_str}) 的極限值。"
        correct_answer = str(a + b)
    else: # level 2, 有理化
        a = random.randint(1, 5)
        a_sq = a*a
        # (sqrt(x) - sqrt(a)) / (x-a) = (sqrt(x)-sqrt(a)) / (sqrt(x)-sqrt(a))(sqrt(x)+sqrt(a)) = 1/(sqrt(x)+sqrt(a))
        num_str = "√x - √a"
        den_str = "x - a"
        question_text = f"請求出 lim (x→{a_sq}) (√x - {a}) / (x - {a_sq}) 的極限值。"
        correct_answer = f"1/{2*a}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer)