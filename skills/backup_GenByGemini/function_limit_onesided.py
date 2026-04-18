# \極限\單邊極限
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「單邊極限」的觀念題。
    """
    a = random.randint(1, 5)
    l = random.randint(1, 10)
    r = random.randint(1, 10)
    while l == r: r = random.randint(1, 10)
    
    question_text = (
        f"已知函數 f(x) 的左極限 lim (x→{a}⁻) f(x) = {l}，右極限 lim (x→{a}⁺) f(x) = {r}。\n"
        "請問 lim (x→{a}) f(x) 的值為何？\n\n"
        f"A) {l}\nB) {r}\nC) 不存在"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')