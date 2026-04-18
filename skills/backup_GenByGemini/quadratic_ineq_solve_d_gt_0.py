# \坐標與函數\二次不等式 (D > 0)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「二次不等式 (D > 0)」的題目。
    """
    alpha = random.randint(-10, 10)
    beta = random.randint(-10, 10)
    while alpha == beta: beta = random.randint(-10, 10)
    if alpha > beta: alpha, beta = beta, alpha

    op = random.choice(['>', '<'])
    
    question_text = f"請求解不等式 (x - {alpha})(x - {beta}) {op} 0。"
    
    if op == '>':
        correct_answer = f"x>{beta}或x<{alpha}"
    else: # op == '<'
        correct_answer = f"{alpha}<x<{beta}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)