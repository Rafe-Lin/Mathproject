# \坐標與函數\二次不等式 (D = 0)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「二次不等式 (D = 0)」的題目。
    """
    alpha = random.randint(-10, 10)
    op = random.choice(['>', '>=', '<', '<='])
    
    question_text = f"請求解不等式 (x - {alpha})² {op} 0。"
    
    if op == '>': correct_answer = f"x≠{alpha}"
    elif op == '>=': correct_answer = "所有實數"
    elif op == '<': correct_answer = "無解"
    else: # op == '<='
        correct_answer = f"x={alpha}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)