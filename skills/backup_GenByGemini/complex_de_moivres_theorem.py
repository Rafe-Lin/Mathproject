# \複數\棣美弗定理
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「棣美弗定理」的題目。
    """
    r = random.randint(1, 2)
    angle = random.choice([15, 30, 45, 60])
    n = random.randint(2, 6)
    
    if level == 1:
        question_text = f"請計算 (cos{angle}° + i sin{angle}°)^{n} 的主輻角是多少度？"
        correct_answer = str((angle * n) % 360)
    else: # level 2
        question_text = f"請計算 [{r}(cos{angle}° + i sin{angle}°)]^{n} 的絕對值是多少？"
        correct_answer = str(r**n)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')