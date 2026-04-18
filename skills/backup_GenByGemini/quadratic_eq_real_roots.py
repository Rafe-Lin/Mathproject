# \方程式\一元二次方程式 (實根解)
import random
import math
from .utils import check_answer

def generate(level=1):
    """
    生成一道「一元二次方程式 (實根解)」的題目。
    """
    if level == 1:
        # 構造可因式分解的題目
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)
        # x² - (r1+r2)x + r1*r2 = 0
        a, b, c = 1, -(r1 + r2), r1 * r2
        question_text = f"請利用因式分解，求解方程式：x² + {b}x + {c} = 0。\n(若有兩解，請用逗號分隔)"
        correct_answer = f"{r1},{r2}"
    else: # level 2, 需要用公式解
        # 構造 D > 0 但不易因式分解的題目
        a = random.randint(1, 3)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        discriminant = b**2 - 4*a*c
        while discriminant <= 0: # 確保有實根
            c = random.randint(-10, 10)
            discriminant = b**2 - 4*a*c
        
        question_text = f"請利用公式法，求解方程式：{a}x² + {b}x + {c} = 0。\n(答案四捨五入至小數點後兩位，若有兩解請用逗號分隔)"
        sol1 = (-b + math.sqrt(discriminant)) / (2*a)
        sol2 = (-b - math.sqrt(discriminant)) / (2*a)
        correct_answer = f"{round(sol1, 2)},{round(sol2, 2)}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_parts = sorted(correct_answer.strip().split(','))
    return check_answer(",".join(user_parts), ",".join(correct_parts))