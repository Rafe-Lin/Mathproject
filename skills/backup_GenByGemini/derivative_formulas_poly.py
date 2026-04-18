# \微分\多項式微分公式
import random
from .utils import check_answer, to_superscript

def generate(level=1):
    """
    生成一道「多項式微分公式」的題目。
    """
    if level == 1:
        n = random.randint(2, 5)
        c = random.randint(2, 10)
        question_text = f"請求出函數 f(x) = {c}x 的導數 f'(x)。"
        correct_answer = str(c)
    else: # level 2
        a, n = random.randint(2, 5), random.randint(2, 5)
        b, m = random.randint(2, 5), random.randint(2, 5)
        question_text = f"請求出函數 f(x) = {a}x^{n} + {b}x^{m} 的導數 f'(x)。"
        correct_answer = f"{a*n}x{to_superscript(n-1)} + {b*m}x{to_superscript(m-1)}".replace("+-", "-")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    # 為了方便使用者輸入，允許 `^` 和 `**`
    user_answer = user_answer.replace(" ", "").replace("**", "").replace("^", "")
    correct_answer_simple = correct_answer.replace(" ", "").replace("²", "2").replace("³", "3").replace("⁴", "4").replace("⁵", "5")
    return check_answer(user_answer, correct_answer_simple)