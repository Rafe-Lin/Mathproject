# \坐標與函數\二次不等式 (D < 0)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「二次不等式 (D < 0)」的題目。
    """
    # 構造一個 D < 0 的二次式: (x-h)² + k, k>0
    h = random.randint(-5, 5)
    k = random.randint(1, 10)
    a, b, c = 1, -2*h, h*h + k
    
    op = random.choice(['>', '>=', '<', '<='])
    
    question_text = f"請求解不等式 {a}x² + {b}x + {c} {op} 0。"
    
    if op in ['>', '>=']:
        correct_answer = "所有實數"
    else: # op in ['<', '<=']
        correct_answer = "無解"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)