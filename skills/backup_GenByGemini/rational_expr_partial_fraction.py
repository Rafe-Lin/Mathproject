# \多項式\部分分式 (拆解)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「部分分式 (拆解)」的題目。
    """
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    while a == b: b = random.randint(1, 5)
    
    # 構造題目: (A(x-b) + B(x-a)) / (x-a)(x-b)
    A = random.randint(1, 3)
    B = random.randint(1, 3)
    
    num_coeff_x = A + B
    num_const = -A*b - B*a
    
    question_text = f"請將分式 ({num_coeff_x}x + {num_const}) / ((x-{a})(x-{b})) 拆解為部分分式 A/(x-{a}) + B/(x-{b})，並求出 A 的值。"
    correct_answer = str(A)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')