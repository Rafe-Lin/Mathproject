# \積分\微積分基本定理 (計算)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「微積分基本定理 (計算)」的題目。
    """
    if level == 1:
        a, b = random.randint(0, 2), random.randint(3, 5)
        c = random.randint(2, 10)
        question_text = f"請計算定積分 ∫ (從 {a} 到 {b}) {c} dx。"
        correct_answer = str(c * (b - a))
    else: # level 2
        a, b = random.randint(0, 2), random.randint(3, 5)
        c = random.randint(2, 5)
        question_text = f"請計算定積分 ∫ (從 {a} 到 {b}) {c}x dx。"
        # F(x) = c/2 * x², F(b)-F(a) = c/2 * (b²-a²)
        correct_answer = str(c/2 * (b**2 - a**2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')