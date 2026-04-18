# \微分\連鎖律
import random
from .utils import check_answer, to_superscript

def generate(level=1):
    """
    生成一道「連鎖律」的題目。
    """
    if level == 1:
        question_text = (
            "根據微分的連鎖律，[g(f(x))]' 等於什麼？\n\n"
            "A) g'(f'(x))\nB) g'(f(x)) · f'(x)\nC) g'(x) · f'(x)"
        )
        correct_answer = "B"
    else: # level 2
        a, n = random.randint(2, 5), random.randint(2, 5)
        question_text = f"請求出函數 h(x) = ({a}x + 1){to_superscript(n)} 的導數 h'(x)。"
        correct_answer = f"{n*a}({a}x+1){to_superscript(n-1)}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        user_answer = user_answer.replace(" ", "").replace("**", "").replace("^", "")
        correct_answer_simple = correct_answer.replace(" ", "").replace("²", "2").replace("³", "3").replace("⁴", "4").replace("⁵", "5")
        return check_answer(user_answer, correct_answer_simple)